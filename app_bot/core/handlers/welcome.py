import datetime
import logging
from aiogram import Bot, types, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, StateFilter, CommandObject
from aiogram_dialog import DialogManager, StartMode
from core.states.agency import AgencyStateGroup
from core.states.manager import ManagerStateGroup
from core.states.bloger import BlogerStateGroup
from core.states.buyer import BuyerStateGroup
from core.utils.texts import set_user_commands, set_admin_commands, _
from core.database.models import User, StatusType, Post, Dispatcher
from core.keyboards.inline import payment_kb
from settings import settings


logger = logging.getLogger(__name__)
router = Router(name='Start router')


@router.message(Command(commands=['start']))
async def start_handler(
        message: types.Message,
        bot: Bot,
        state: FSMContext,
        dialog_manager: DialogManager,
        command: CommandObject,
):
    await state.clear()
    try:
        await dialog_manager.reset_stack()
    except:
        pass

    # go to dialogs if already registered
    user = await User.get_or_none(user_id=message.from_user.id)
    if user and user.status and user.status in StatusType:
        if user.status == StatusType.agency:
            await set_admin_commands(bot=bot, scope=types.BotCommandScopeChat(chat_id=message.from_user.id))
            await dialog_manager.start(state=AgencyStateGroup.menu, mode=StartMode.RESET_STACK)
        elif user.status == StatusType.manager:
            await dialog_manager.start(state=ManagerStateGroup.menu, mode=StartMode.RESET_STACK)
        elif user.status == StatusType.bloger:
            await dialog_manager.start(state=BlogerStateGroup.menu, mode=StartMode.RESET_STACK)
        elif user.status == StatusType.buyer:
            await dialog_manager.start(state=BuyerStateGroup.menu, mode=StartMode.RESET_STACK)

        return


    await set_user_commands(bot=bot, scope=types.BotCommandScopeChat(chat_id=message.from_user.id))

    # default welcome
    if not command.args:
        agency_url = await bot.create_invoice_link(
            title=_('AGENCY_INVOICE_TITLE'),
            description=_('AGENCY_INVOICE_DESCRIPTION'),
            provider_token=settings.payments_provider_token.get_secret_value(),
            currency='rub',
            prices=[types.LabeledPrice(label=_('AGENCY_INVOICE_TITLE'), amount=2999 * 100)],
            payload=f'agency'
            )
        manager_url = await bot.create_invoice_link(
            title=_('MANAGER_INVOICE_TITLE'),
            description=_('MANAGER_INVOICE_DESCRIPTION'),
            provider_token=settings.payments_provider_token.get_secret_value(),
            currency='rub',
            prices=[types.LabeledPrice(label=_('MANAGER_INVOICE_TITLE'), amount=399 * 100)],
            payload=f'manager'
            )

        await message.answer(
            text=_('WELCOME_MSG'),
            reply_markup=payment_kb(agency_url=agency_url, manager_url=manager_url)
        )

    # add bloger/manager/buyer
    else:
        link = settings.bot_link + command.args
        user = await User.get_or_none(link=link)
        if not user:  # ignore start w/o link from non-users
            return

        # save tg data and delete link
        user.user_id = message.from_user.id
        user.username = message.from_user.username
        user.link = None
        await user.save()

        # start manager/bloger/buyer dialog
        if user.status == StatusType.manager:
            await dialog_manager.start(state=ManagerStateGroup.menu, mode=StartMode.RESET_STACK)
        elif user.status == StatusType.bloger:
            await dialog_manager.start(state=BlogerStateGroup.menu, mode=StartMode.RESET_STACK)
        elif user.status == StatusType.buyer:
            await dialog_manager.start(state=BuyerStateGroup.menu, mode=StartMode.RESET_STACK)
