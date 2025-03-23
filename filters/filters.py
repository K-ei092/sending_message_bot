from aiogram.filters import BaseFilter
from aiogram.types import Message
from sqlalchemy import Boolean

from sqlalchemy.ext.asyncio.engine import AsyncEngine

from database.worker import WorkerDB

from config_data.config import ConfigBot, load_config_bot


config: ConfigBot = load_config_bot()
admin_ids: list[int] = config.tg_bot.admin_ids


# фильтр проверят на админа
class IsAdmins(BaseFilter):
    def __init__(self) -> None:
        self.admin_ids = admin_ids
    async def __call__(self, message: Message) -> bool:
        return message.from_user.id in self.admin_ids


# фильтр проверяет добавлен ли ранее пользователь в базу ранее
class IsOldUser(BaseFilter):
    async def __call__(self, message: Message, db_engine: AsyncEngine) -> bool:
        wk = WorkerDB(db_engine)
        user_id = message.from_user.id
        result: bool = await wk.check_user_id(user_id)
        return result
