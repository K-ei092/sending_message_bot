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
from database.worker import WorkerDB
from handlers.func.func_handlers import delete_message
from keyboards.kb import create_keyboar
from lexicon.lexicon import LEXICON


router = Router()


logger = logging.getLogger(__name__)


# хэндлер на команду "/admin_help" и в ответ инструкции
@router.message(Command(commands='admin_help'), IsAdmins(), StateFilter(default_state))
async def process_admin_command_help(message: Message):
    await message.answer(text=LEXICON[message.text])


# хэндлер на команду "/user_database" и в ответ файл с данными пользователей
@router.message(Command(commands='user_database'), IsAdmins(), StateFilter(default_state))
async def process_admin_command_user_database(message: Message, db_engine: AsyncEngine):
    wk = WorkerDB(db_engine)
    file_name = await wk.get_db()
    file = FSInputFile(file_name)
    await message.answer_document(file)
    if os.path.isfile(file_name):
        os.remove(file_name)


# хэндлер на команду "УДАЛИТЬ ID пользователя"
@router.message(F.text.startswith('УДАЛИТЬ'), IsAdmins(), StateFilter(default_state))
async def process_delete_user_database(message: Message, db_engine: AsyncEngine, scheduler: AsyncIOScheduler, state: FSMContext):
    telegram_id = int(message.text.split()[1])
    for i in range(1, 4):
        try:
            scheduler.remove_job(job_id=f'{telegram_id}_{i}')
        except Exception as e:
            logger.error(f'Failed to remove scheduler job: {e}')
    await state.clear()
    wk = WorkerDB(db_engine)
    await wk.delete_user(telegram_id)
    await message.answer(text=LEXICON['delete_user'])


# хэндлер на любое сообщение админа
@router.message(IsAdmins(), ~CommandStart(), ~Command(commands='help'),
                ~Command(commands='statistic'), StateFilter(default_state), ~Command(commands='restart'))
async def process_admin_message_for_users(message: Message):
    message_id_for_users = message.message_id
    my_keyboard = create_keyboar(message_id_for_users)
    await message.answer(text=LEXICON['admin_message_for_users'], reply_markup=my_keyboard)


# хэндлер на инлайн-клавиатуру подтверждения админом ОТПРАВИТЬ ВСЕМ сообщение
@router.callback_query(F.data.startswith('YES^'))
async def process_forward_message(callback: CallbackQuery, bot: Bot, db_engine: AsyncEngine):
    wk = WorkerDB(db_engine)
    admin_id = callback.from_user.id
    message_id_for_users = int(callback.data[4:])
    users_id = await wk.get_all_tg_id()
    users_id_who_except = []
    for chat_id in users_id:
        if chat_id != admin_id:
            try:
                await bot.forward_message(chat_id=chat_id, from_chat_id=admin_id,
                                          message_id=message_id_for_users, request_timeout=20)
            except TelegramForbiddenError as e:
                if 'blocked by the user' in str(e):
                    await wk.delete_user(int(chat_id))
            except Exception as e:
                users_id_who_except.append(chat_id)
                logger.error(f'Ошибка при пересылке сообщения от админа пользователям {e}', exc_info=True)
    if users_id_who_except:
        await callback.message.edit_text(text=f'Ошибка: не переслано пользователям {users_id_who_except}')
    else:
        await callback.message.edit_text(text=LEXICON['message_forward'])


# хэндлер хна инлайн-клавиатуру выбора админом варианта НЕ ПЕРЕСЫЛАТЬ СООБЩЕНИЕ
@router.callback_query(F.data.startswith('NO^'))
async def process_not_forward_message(callback: CallbackQuery):
    await callback.message.answer(text=LEXICON['do_not_send'])


# хэндлер на команду "/statistic"
@router.message(Command(commands='statistic'), IsAdmins(), StateFilter(default_state))
async def process_statistic(message: Message, bot: Bot, db_engine: AsyncEngine):
    wk = WorkerDB(db_engine)
    rating_text = await wk.get_statistic(message.from_user.id)
    logger.info(rating_text)
    msg = await message.answer(text=rating_text)
    user_id = message.from_user.id
    from_msg_del = msg.message_id
    await delete_message(bot=bot, from_msg_del=from_msg_del, user_id=user_id, time_sleep=60 * 3, amount_msg_del=2)
