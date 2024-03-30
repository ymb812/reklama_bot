from aiogram_dialog import DialogManager
from core.database.models import User


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
