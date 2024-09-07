import asyncio
import logging

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest


logger = logging.getLogger(__name__)


async def delete_message(bot: Bot, from_msg_del: int, user_id: int, time_sleep: int = 5, amount_msg_del: int = 2):

    await asyncio.sleep(time_sleep)

    for i in range(from_msg_del, from_msg_del - amount_msg_del, -1):

        try:
            await bot.delete_message(user_id, i, request_timeout=30)
            await asyncio.sleep(1)

        except TelegramBadRequest as ex:
            if ex.message == "Bad Request: message to delete not found":
                pass

        except Exception:
            logger.error(
                f'Ошибка при удалении сообщения user_id - {user_id}, message_id - {i}',
                exc_info=True
            )
