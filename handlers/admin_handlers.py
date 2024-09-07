import os
import logging

from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message, FSInputFile, CallbackQuery
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.exceptions import TelegramForbiddenError
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from sqlalchemy.ext.asyncio.engine import AsyncEngine

from filters.filters import IsAdmins
from database.table_processing import get_file_db, get_all_user_id, delete_user_database, get_statistic
from handlers.func.func_handlers import delete_message
from keyboards.kb import create_keyboar
from lexicon.lexicon import LEXICON


router = Router()


logger = logging.getLogger(__name__)


# хэндлер на команду "/admin_help"
# и отправлять в ответ инструкции
@router.message(Command(commands='admin_help'), IsAdmins(), StateFilter(default_state))
async def process_admin_command_help(message: Message):
    await message.answer(text=LEXICON[message.text])


# хэндлер на команду "/user_database"
# и отправлять в ответ файл с данными пользователей
@router.message(Command(commands='user_database'), IsAdmins(), StateFilter(default_state))
async def process_admin_command_user_database(message: Message, db_engine: AsyncEngine):
    file_name = await get_file_db(db_engine)
    file = FSInputFile(file_name)
    await message.answer_document(file)
    if os.path.isfile(file_name):
        os.remove(file_name)


# хэндлер на команду "УДАЛИТЬ ID пользователя"
# и отправлять в ответ файл с данными пользователей
@router.message(F.text.startswith('УДАЛИТЬ'), IsAdmins(), StateFilter(default_state))
async def process_delete_user_database(
        message: Message,
        db_engine: AsyncEngine,
        scheduler: AsyncIOScheduler,
        state: FSMContext
):
    telegram_id = int(message.text.split()[1])

    try:
        for i in range(1, 5):
            scheduler.remove_job(f'{telegram_id}_{i}')
    except Exception:
        pass
    await state.clear()
    res = await delete_user_database(db_engine, telegram_id)
    if res:
        await message.answer(text=LEXICON['delete_user'])


# хэндлер на любое сообщение админа
# и после подтверждения пересылать его всем своим пользователям
@router.message(IsAdmins(), ~CommandStart(), ~Command(commands='help'),
                ~Command(commands='statistic'), StateFilter(default_state), ~Command(commands='restart'))
async def process_admin_message_for_users(message: Message):
    message_id_for_users = message.message_id
    my_keyboard = create_keyboar(message_id_for_users)
    await message.answer(text=LEXICON['admin_message_for_users'], reply_markup=my_keyboard)


# хэндлер на инлайн-клавиатуру подтверждения админом ОТПРАВИТЬ ВСЕМ сообщение
@router.callback_query(F.data.startswith('YES^'))
async def process_forward_message(callback: CallbackQuery, bot: Bot, db_engine: AsyncEngine):
    admin_id = callback.from_user.id
    message_id_for_users = int(callback.data[4:])
    # получаем список пользователей
    list_user_id = await get_all_user_id(db_engine)
    users_id_who_except = []
    for chat_id in list_user_id:
        if chat_id != admin_id:
            try:
                await bot.forward_message(chat_id=chat_id, from_chat_id=admin_id,
                                          message_id=message_id_for_users, request_timeout=20)
            except TelegramForbiddenError as e:
                # удаляем пользователя из базы, если он заблокировал бота
                if 'blocked by the user' in str(e):
                    await delete_user_database(db_engine, int(chat_id))
            except Exception:
                users_id_who_except.append(chat_id)
                logger.error(f'Ошибка при пересылке сообщения от админа пользователям', exc_info=True)
    if users_id_who_except:
        await callback.message.edit_text(text=f'Ошибка: не переслано пользователям {users_id_who_except}')
    else:
        await callback.message.edit_text(text=LEXICON['message_forward'])


# хэндлер на инлайн-клавиатуру выбора админом варианта НЕ ПЕРЕСЫЛАТЬ СООБЩЕНИЕ
@router.callback_query(F.data.startswith('NO^'))
async def process_not_forward_message(callback: CallbackQuery):
    await callback.message.answer(text=LEXICON['do_not_send'])


# хэндлер на команду "/statistic"
@router.message(Command(commands='statistic'), IsAdmins(), StateFilter(default_state))
async def process_statistic(message: Message, bot: Bot, db_engine: AsyncEngine):
    rating_text = await get_statistic(db_engine, message.from_user.id)
    msg = await message.answer(text=rating_text)
    user_id = message.from_user.id
    from_msg_del = msg.message_id
    await delete_message(bot=bot, from_msg_del=from_msg_del, user_id=user_id, time_sleep=60 * 3, amount_msg_del=2)
