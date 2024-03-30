from aiogram.types import ContentType
from aiogram_dialog import DialogManager
from aiogram_dialog.api.entities import MediaAttachment
from core.database.models import User, Advertisement


async def get_input_data(dialog_manager: DialogManager, **kwargs):
    data = dialog_manager.dialog_data
    return {'data': data}


async def get_users(dialog_manager: DialogManager, **kwargs):
    users = await User.filter(status=dialog_manager.dialog_data['type']).all()

    return {
        'users': users
    }


async def get_user(dialog_manager: DialogManager, **kwargs):
    user = await User.get_or_none(id=dialog_manager.dialog_data['user_id'])
    if not user:
        raise ValueError

    return {
        'user': user
    }


async def get_reklams_by_status(dialog_manager: DialogManager, **kwargs) -> dict[str, list[Advertisement]]:
    current_page = await dialog_manager.find('reklam_scroll').get_page()

    if not dialog_manager.dialog_data.get('is_paid'):
        reklams = await Advertisement.filter(is_approved_by_bloger=False).all()
    else:
        reklams = await Advertisement.filter(is_paid=True).all()
    if not reklams:
        raise ValueError

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

    return {
        'pages': len(reklams),
        'current_page': current_page + 1,
        'media_content': media_content,
        'description':  current_reklam.text,
    }
