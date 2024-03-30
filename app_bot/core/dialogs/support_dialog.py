from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.text import Const
from aiogram_dialog.widgets.input import TextInput
from core.dialogs.callbacks import CallBackHandler
from core.states.manager import ManagerStateGroup
from core.utils.texts import _


support_dialog = Dialog(
    # question input
    Window(
        Const(text=_('QUESTION_INPUT')),
        TextInput(
            id='create_bloger_link',
            type_factory=str,
            on_success=CallBackHandler.entered_username,
        ),
        state=ManagerStateGroup.create_bloger_link,
    ),
)
