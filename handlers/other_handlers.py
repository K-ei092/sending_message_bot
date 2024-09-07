from aiogram import Router, Bot
from aiogram.types import Message

from handlers.func.func_handlers import delete_message

router = Router()


# хэндлер на любые сообщения пользователя,
# не предусмотренные логикой работы бота
@router.message()
async def send_echo(message: Message, bot: Bot):
    msg = await message.answer(text=f'Мне неизвестна команда "{message.text}"\nПопробуй набрать /start или /help')
    user_id = message.from_user.id
    from_msg_del = msg.message_id
    await delete_message(bot=bot, from_msg_del=from_msg_del, user_id=user_id, time_sleep=60, amount_msg_del=2)
