import asyncio
from random import randint

from aiogram import Router, Bot, F
from aiogram.filters import CommandStart, Command, StateFilter, ChatMemberUpdatedFilter, KICKED
from aiogram.types import Message, CallbackQuery, ChatMemberUpdated
from aiogram.fsm.context import FSMContext

from sqlalchemy.ext.asyncio.engine import AsyncEngine
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from filters.filters import IsOldUser, IsAdmins
from fsm.fsm_mode import FSMFillForm
from aiogram.fsm.state import default_state

from database.table_processing import (
    add_new_user,
    reset_user_count,
    change_exercise_state,
    increase_record,
    delete_user_database
)

from handlers.func.func_handlers import delete_message
from keyboards.kb import (
    create_keyboard_time_zone,
    create_keyboard_day_scheduler,
    create_keyboard_time_scheduler,
    create_keyboard_first_exercise,
    create_update,
    create_keyboard_confirm_restart
)

from lexicon.lexicon import LEXICON

from service.sending import send_exercise, send_self_gratitude, send_reminder

router = Router()


# хэндлер на апдейт блокировки бота пользователем и удаляет данные о нём из БД
@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=KICKED))
async def user_blocked_bot(
        event: ChatMemberUpdated,
        db_engine: AsyncEngine,
        scheduler: AsyncIOScheduler,
        state: FSMContext
):
    telegram_id = event.from_user.id
    try:
        for i in range(1, 5):
            scheduler.remove_job(f'{telegram_id}_{i}')
    except Exception:
        pass

    await state.clear()
    await delete_user_database(db_engine, telegram_id)


# хэндлер на команду "/restart" и удаляет все данные о пользователе после подтверждения
@router.message(Command(commands='restart'), IsOldUser())
async def process_restart_command(message: Message, ):
    my_keyboard = create_keyboard_confirm_restart()
    await message.answer(text=LEXICON['confirm_restart'], reply_markup=my_keyboard)


# хэндлер на подтверждение пользователем удаления из БД
@router.callback_query(F.data == '^confirm_restart^')
async def process_confirm_restart(
        callback: CallbackQuery,
        db_engine: AsyncEngine,
        scheduler: AsyncIOScheduler,
        state: FSMContext
):
    telegram_id = callback.from_user.id
    try:
        for i in range(1, 5):
            scheduler.remove_job(f'{telegram_id}_{i}')
    except Exception:
        pass

    await state.clear()
    res = await delete_user_database(db_engine, telegram_id)
    if res:
        await callback.message.edit_text(text=LEXICON['restart'])


# хэндлер на отмену пользователем удаления из БД
@router.callback_query(F.data == '^confirm_restart_not^')
async def process_confirm_restart_not(callback: CallbackQuery):
    await callback.message.edit_text(text=LEXICON['not_restart'])
    await asyncio.sleep(3)
    await callback.message.delete()


# хэндлер на команду "/start" для нового пользователя
@router.message(CommandStart(), StateFilter(default_state), ~IsOldUser())
async def process_start_command(message: Message, db_engine: AsyncEngine, state: FSMContext):
    telegram_id = message.from_user.id
    telegram_name = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    await add_new_user(db_engine, telegram_id, telegram_name, first_name, last_name)

    await message.answer(text=LEXICON[message.text])
    await asyncio.sleep(3)
    my_keyboard = create_keyboard_time_zone()
    await message.answer(text=LEXICON['time_zone'], reply_markup=my_keyboard)
    await state.set_state(FSMFillForm.fill_tz)


# хэндлер на выбранную TZ и предложит выбрать дни недели
@router.callback_query(StateFilter(FSMFillForm.fill_tz), ~StateFilter(default_state))
async def process_tz_press(callback: CallbackQuery, state: FSMContext):
    await state.update_data(fill_tz=callback.data)
    await callback.message.delete()
    await asyncio.sleep(2)
    my_keyboard = create_keyboard_day_scheduler()
    await callback.message.answer(text=LEXICON['day_scheduler'], reply_markup=my_keyboard)
    await state.set_state(FSMFillForm.fill_day_scheduler)


# хэндлер на выбранные дни недели и предложит выбрать время
@router.callback_query(StateFilter(FSMFillForm.fill_day_scheduler), ~StateFilter(default_state))
async def process_day_scheduler_press(callback: CallbackQuery, state: FSMContext):
    await state.update_data(fill_day_scheduler=callback.data)
    await callback.message.delete()
    await asyncio.sleep(2)
    my_keyboard = create_keyboard_time_scheduler()
    await callback.message.answer(text=LEXICON['time_scheduler'], reply_markup=my_keyboard)
    await state.set_state(FSMFillForm.fill_time_scheduler)


# Этот хэндлер будет срабатывать на выбранное время, заносить все сведения в планировщика, очищать FSM,
# и отправлять предложение на выбор задание "сейчас" или "потом"
@router.callback_query(StateFilter(FSMFillForm.fill_time_scheduler), ~StateFilter(default_state))
async def process_time_scheduler_press(callback: CallbackQuery, state: FSMContext, scheduler: AsyncIOScheduler):
    await state.update_data(fill_time_scheduler=callback.data)
    await callback.message.delete()
    await asyncio.sleep(2)
    await callback.message.answer(text=LEXICON['end_sitings'])
    await asyncio.sleep(5)

    telegram_id = callback.from_user.id
    time_zone = (await state.get_data())['fill_tz']
    day_of_week = (await state.get_data())['fill_day_scheduler']
    time_scheduler = (await state.get_data())['fill_time_scheduler']

    await state.clear()

    hour = int(time_scheduler)

    scheduler.add_job(send_exercise, 'cron', day_of_week=day_of_week, hour=hour, timezone=time_zone,
                      id=f'{telegram_id}_1', kwargs={'user_id': telegram_id},
                      misfire_grace_time=60 * 5, max_instances=3)
    scheduler.add_job(send_self_gratitude, 'cron', day_of_week=day_of_week, hour='20', timezone=time_zone,
                      id=f'{telegram_id}_2', kwargs={'user_id': telegram_id},
                      misfire_grace_time=60 * 5, max_instances=3)
    scheduler.add_job(send_reminder, 'cron', day_of_week='mon-sat', hour=15, minute=15, timezone=time_zone,
                      id=f'{telegram_id}_3', kwargs={'user_id': telegram_id},
                      misfire_grace_time=60 * 5, max_instances=3)

    await asyncio.sleep(2)
    my_keyboard = create_keyboard_first_exercise()
    await callback.message.answer(text=LEXICON['first_exercise'], reply_markup=my_keyboard)


# Этот хэндлер будет срабатывать на инлайн-клавиатуру согласия пользователя на первое задание
@router.callback_query(F.data == '^now^')
async def process_reset_user_count(callback: CallbackQuery, bot: Bot, db_engine: AsyncEngine):
    user_id = callback.from_user.id
    await callback.message.edit_text(text=LEXICON['first_exercise_now_callback'])
    await asyncio.sleep(5)
    await send_exercise(bot, db_engine, user_id)


# Этот хэндлер будет срабатывать на инлайн-клавиатуру отказа пользователя от первого задания
@router.callback_query(F.data == '^late^')
async def process_not_reset_user_count(callback: CallbackQuery):
    await callback.message.edit_text(text=LEXICON['first_exercise_late_callback'])


# Этот хэндлер будет срабатывать на любое действие в ходе настроек FSM, кроме /restart и блокировки бота
@router.message(~StateFilter(default_state))
async def process_state_error(message: Message, bot: Bot):
    msg = await message.answer(text=LEXICON['state_error'])
    user_id = message.from_user.id
    from_msg_del = msg.message_id
    await delete_message(bot=bot, from_msg_del=from_msg_del, user_id=user_id, time_sleep=15, amount_msg_del=2)


# Этот хэндлер будет срабатывать на команду "/help"
@router.message(Command(commands='help'), StateFilter(default_state))
async def process_help(message: Message, bot: Bot):
    msg = await message.answer(text=LEXICON[message.text])
    user_id = message.from_user.id
    from_msg_del = msg.message_id
    await delete_message(bot=bot, from_msg_del=from_msg_del, user_id=user_id, time_sleep=60 * 2, amount_msg_del=2)


# Этот хэндлер будет срабатывать на команду "/start" для пользователя, который уже есть в базе
# и предлагать запуск нового блока заданий
@router.message(CommandStart(), IsOldUser(), ~Command(commands='admin_help'), StateFilter(default_state))
async def process_start_command_old(message: Message):
    my_keyboard = create_update()
    await message.answer(text=LEXICON['old_user'], reply_markup=my_keyboard)


# Этот хэндлер будет срабатывать на инлайн-клавиатуру выбора пользователем выполнения нового блока заданий
@router.callback_query(F.data == '^yes^')
async def process_reset_user_count(callback: CallbackQuery, bot: Bot, db_engine: AsyncEngine):
    user_id = callback.from_user.id
    await reset_user_count(db_engine, user_id)
    await callback.message.edit_text(text=LEXICON['reset_counter'])
    user_id = callback.from_user.id
    from_msg_del = callback.message.message_id
    await delete_message(bot=bot, from_msg_del=from_msg_del, user_id=user_id, time_sleep=4, amount_msg_del=2)
    await asyncio.sleep(1)
    await send_exercise(bot, db_engine, user_id)


# Этот хэндлер будет срабатывать на инлайн-клавиатуру отказа пользователя от выполнения нового блока заданий
@router.callback_query(F.data == '^no^')
async def process_not_reset_user_count(callback: CallbackQuery, bot: Bot):
    await callback.message.edit_text(text=LEXICON['not_update_counter'])
    user_id = callback.from_user.id
    from_msg_del = callback.message.message_id
    await delete_message(bot=bot, from_msg_del=from_msg_del, user_id=user_id, time_sleep=5, amount_msg_del=2)


# Этот хэндлер будет срабатывать на инлайн-клавиатуру подтверждения пользователем выполнения задания (поставил лайк)
@router.callback_query(F.data == 'recommendation_implemented')
async def process_change_exercise_state(callback: CallbackQuery, bot: Bot, db_engine: AsyncEngine):
    user_id = callback.from_user.id
    await change_exercise_state(db_engine, callback.from_user.id, True)
    await callback.message.edit_text(
        text=LEXICON['change_exercise_state'][randint(1, len(LEXICON['change_exercise_state']) - 1)]
    )
    await increase_record(db_engine, user_id)
    from_msg_del = callback.message.message_id
    await delete_message(bot=bot, from_msg_del=from_msg_del, user_id=user_id, time_sleep=60 * 2, amount_msg_del=1)


# Этот хэндлер будет реагировать на команду /admin_help не от администратора
@router.message(Command(commands='admin_help'), ~IsAdmins())
async def send_echo(message: Message, bot: Bot):
    msg = await message.answer(text=f'Команда "{message.text}" для администраторов бота\nПопробуй набрать /help')
    user_id = message.from_user.id
    from_msg_del = msg.message_id
    await delete_message(bot=bot, from_msg_del=from_msg_del, user_id=user_id, time_sleep=10, amount_msg_del=2)