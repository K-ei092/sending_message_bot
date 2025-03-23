import asyncio

from aiogram import Router, Bot
from aiogram.types import Message


router = Router()


# хэндлер на любые сообщения пользователя, не предусмотренные логикой работы
@router.message()
async def send_echo(message: Message, bot: Bot):
    msg = await message.answer(text=f'Мне неизвестна команда "{message.text}"\nПопробуй набрать /start или /help')
    await asyncio.sleep(30)
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    await msg.delete()
