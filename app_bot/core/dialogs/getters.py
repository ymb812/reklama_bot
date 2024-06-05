from datetime import datetime
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

    # if clicked for full blogers list
    if get_dialog_data(dialog_manager=dialog_manager, key='is_full_blogers_list'):
        dialog_manager.dialog_data['is_full_blogers_list'] = False  # clean data
        users = await User.filter(
            status=status, agency_id=agency_or_manager.agency_id,
        ).all()

    else:
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

    reklams_sum = sum(adv.price for adv in await Advertisement.filter(manager_id=user_id))

    return {
        'user': user,
        'reklams_sum': reklams_sum,
    }

async def get_manager(dialog_manager: DialogManager, **kwargs):
    user = await User.get_or_none(user_id=dialog_manager.event.from_user.id)
    return {
        'user': user,
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


async def get_stats_by_period(dialog_manager: DialogManager, **kwargs):
    agency = await User.get(user_id=dialog_manager.event.from_user.id)

    start_date = datetime.strptime(dialog_manager.dialog_data['start_date_str'], '%d.%m.%Y')
    end_date = datetime.strptime(dialog_manager.dialog_data['end_date_str'], '%d.%m.%Y')

    advertisements = await Advertisement.filter(
        agency_id=agency.id,
        created_at__gte=start_date,
        created_at__lte=end_date,
    ).all()

    full_income, managers_income, clear_income = 0, 0, 0
    for adv in advertisements:
        manager: User = await adv.manager

        full_income += adv.price
        managers_income += round(adv.price * manager.manager_percent / 100)

    return {
        'full_income': full_income,
        'managers_income': managers_income,
        'clear_income': full_income - managers_income,
        'advertisements_amount': len(advertisements),
    }


async def get_manager_stats_by_period(dialog_manager: DialogManager, **kwargs):
    manager = await User.get(user_id=dialog_manager.event.from_user.id)

    start_date = datetime.strptime(dialog_manager.dialog_data['start_date_str'], '%d.%m.%Y')
    end_date = datetime.strptime(dialog_manager.dialog_data['end_date_str'], '%d.%m.%Y')

    advertisements = await Advertisement.filter(
        agency_id=None,
        manager_id=manager.id,
        created_at__gte=start_date,
        created_at__lte=end_date,
    ).all()

    full_income = 0
    for adv in advertisements:
        full_income += adv.price

    return {
        'full_income': full_income,
        'advertisements_amount': len(advertisements),
    }