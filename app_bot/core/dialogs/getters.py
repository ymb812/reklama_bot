from aiogram.types import ContentType
from aiogram_dialog import DialogManager
from aiogram_dialog.api.entities import MediaAttachment
from tortoise.expressions import Q
from core.database.models import User, Advertisement, UserStats
from core.dialogs.custom_content import get_dialog_data


async def get_input_data(dialog_manager: DialogManager, **kwargs):
    data = dialog_manager.dialog_data
    return {'data': data}


async def get_users(dialog_manager: DialogManager, **kwargs):
    agency_or_manager = await User.get(user_id=dialog_manager.event.from_user.id)

    status = get_dialog_data(dialog_manager=dialog_manager, key='type')
    users = await User.filter(
        Q(status=status) & ((Q(agency_id=agency_or_manager.id) | Q(manager_id=agency_or_manager.id)))
    ).all()

    return {
        'users': users
    }


async def get_user(dialog_manager: DialogManager, **kwargs):
    user_id = get_dialog_data(dialog_manager=dialog_manager, key='user_id')
    user = await User.get_or_none(id=user_id)
    if not user:
        raise ValueError

    return {
        'user': user
    }


async def get_reklams_by_status(dialog_manager: DialogManager, **kwargs) -> dict[str, list[Advertisement]]:
    current_page = await dialog_manager.find('reklam_scroll').get_page()

    # reklams for buyer
    if get_dialog_data(dialog_manager=dialog_manager, key='data_for_buyer'):
        reklams = await Advertisement.filter(buyer__user_id=dialog_manager.event.from_user.id).all()

    # reklams for manager and agency
    elif get_dialog_data(dialog_manager=dialog_manager, key='data_for_manager'):
        # agency
        if get_dialog_data(dialog_manager=dialog_manager, key='is_agency'):
            # get agency reklams by manager
            manager_id = get_dialog_data(dialog_manager=dialog_manager, key='manager_by_agency_id')
            if manager_id:
                reklams = await Advertisement.filter(manager_id=manager_id).all()

            # get agency reklams
            else:
                reklams = await Advertisement.filter(agency__user_id=dialog_manager.event.from_user.id).all()

        # manager
        else:
            reklams = await Advertisement.filter(manager__user_id=dialog_manager.event.from_user.id).all()

    # reklams for bloger
    else:
        if dialog_manager.dialog_data.get('is_paid'):
            reklams = await Advertisement.filter(
                bloger__user_id=dialog_manager.event.from_user.id, is_paid=True,
            ).all()

        else:
            reklams = await Advertisement.filter(
                bloger__user_id=dialog_manager.event.from_user.id, is_approved_by_bloger=False, is_rejected=False,
            ).all()

    if not reklams:
        raise ValueError


    if len(reklams) == 1:
        current_page = 0  # bypass error if we dynamically delete page
    current_reklam = reklams[current_page]

    media_content = None
    if current_reklam.document_file_id:
        media_content = MediaAttachment(ContentType.DOCUMENT, url=current_reklam.document_file_id)
    elif current_reklam.video_file_id:
        media_content = MediaAttachment(ContentType.VIDEO, url=current_reklam.video_file_id)
    elif current_reklam.photo_file_id:
        media_content = MediaAttachment(ContentType.PHOTO, url=current_reklam.photo_file_id)

    dialog_manager.dialog_data['pages'] = len(reklams)
    dialog_manager.dialog_data['current_reklam_id'] = current_reklam.id


    # get data for manager
    data_for_manager = None                                                    # TODO: AFTER 'or' IS TMP FOR BUYER
    if get_dialog_data(dialog_manager=dialog_manager, key='data_for_manager') or get_dialog_data(dialog_manager=dialog_manager, key='data_for_buyer'):
        data_for_manager = {
            'id': current_reklam.id,
            'description': current_reklam.text,
            'is_approved_by_bloger': current_reklam.is_approved_by_bloger,
            'is_paid': current_reklam.is_paid,
            'bloger_tg_username': (await current_reklam.bloger).username if (await current_reklam.bloger) else None,
            'bloger_inst_username': (await current_reklam.bloger).inst_username if (await current_reklam.bloger) else None,
            'buyer_tg_username': (await current_reklam.buyer).username if (await current_reklam.buyer) else None,
        }
        data_for_manager = f'<b>ID</b>: {data_for_manager["id"]}\n' \
                           f'{data_for_manager["description"]}\n\n' \
                           f'{"Согласовано с блогером" if data_for_manager["is_approved_by_bloger"] else "Не согласовано с блогером"}\n' \
                           f'{"Оплачено" if data_for_manager["is_paid"] else "Не оплачено"}\n\n' \
                           f'ТГ блогера: {data_for_manager["bloger_tg_username"]}\n' \
                           f'Inst блогера: {data_for_manager["bloger_inst_username"]}\n' \
                           f'ТГ заказчика: {data_for_manager["buyer_tg_username"]}\n'

    return {
        'pages': len(reklams),
        'current_page': current_page + 1,
        'media_content': media_content,
        'id': current_reklam.id,
        'description':  current_reklam.text,
        'data_for_manager': data_for_manager,
        'is_paid': current_reklam.is_paid,
    }


async def get_user_stats(dialog_manager: DialogManager, **kwargs):
    # handle manager or bloger request
    user_id = get_dialog_data(dialog_manager=dialog_manager, key='user_id')  # from manager
    if user_id:
        user_stats = await UserStats.get_or_none(user_id=user_id)
    else:
        user_stats = await UserStats.get_or_none(user__user_id=dialog_manager.event.from_user.id)   # from bloger


    media_content = None
    if user_stats and user_stats.document_file_id:
        media_content = MediaAttachment(ContentType.DOCUMENT, url=user_stats.document_file_id)
    elif user_stats and user_stats.video_file_id:
        media_content = MediaAttachment(ContentType.VIDEO, url=user_stats.video_file_id)

    return {
        'media_content': media_content
    }
