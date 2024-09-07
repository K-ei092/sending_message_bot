import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

if os.name == 'nt':
    from aiogram.fsm.storage.memory import MemoryStorage
else:
    from aiogram.fsm.storage.redis import RedisStorage, Redis

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio.engine import AsyncEngine

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler_di import ContextSchedulerDecorator

from handlers import other_handlers, user_handlers, admin_handlers
from keyboards.main_menu import set_main_menu

from database.tables import metadata

from config_data.config import ConfigBot, ConfigDB, load_config_bot, load_config_db


# Инициализируем логгер
logger = logging.getLogger(__name__)


# Функция конфигурирования и запуска бота
async def main():

    # Конфигурируем логирование
    logging.basicConfig(
        level=logging.WARNING,                             # настройка - DEBUG, production - WARNING
        filename="logs.log",                               # добавляем логи в файл
        filemode='w',                                      # режим записи (a - добавить, w - переписать)
        format='%(filename)s:%(lineno)d #%(levelname)-8s '
               '[%(asctime)s] - %(name)s - %(message)s')

    # Выводим в консоль информацию о начале запуска бота
    logger.info('Starting bot')

    # Загружаем конфиг
    config_bot: ConfigBot = load_config_bot()
    config_db: ConfigDB = load_config_db()

    # инициализируем соединение СУБД и создание таблицы
    db_engine = create_async_engine(
        url=config_db.database.dsn,
        echo=config_db.database.is_echo,
        pool_size=15,
        max_overflow=-1,
        pool_timeout=45
    )

    async with db_engine.begin() as conn:
        # await conn.run_sync(metadata.drop_all)
        await conn.run_sync(metadata.create_all)

    # Инициализируем хранилище для FSM
    if os.name == 'nt':
        storage = MemoryStorage()
    else:
        # Инициализируем Redis
        aio_redis = Redis(host='localhost')
        storage = RedisStorage(redis=aio_redis)

    # Инициализируем бот и диспетчер
    bot = Bot(
        token=config_bot.tg_bot.token,
        default=DefaultBotProperties(parse_mode='HTML')          # 'MarkdownV2'
    )

    # Настраиваем главное меню бота
    await set_main_menu(bot)

    # настраиваем хранилище для тасков

    job_stores = {
        'default': RedisJobStore()
    }

    # Оборачиваем AsyncIOScheduler специальным классом
    scheduler = ContextSchedulerDecorator(AsyncIOScheduler(jobstores=job_stores))

    # Добавляем зависимости таска в некий контекст
    scheduler.ctx.add_instance(bot, declared_class=Bot)
    scheduler.ctx.add_instance(db_engine, declared_class=AsyncEngine)

    dp = Dispatcher(storage=storage, db_engine=db_engine, scheduler=scheduler)

    # Регистриуем роутеры в диспетчере
    dp.include_router(admin_handlers.router)
    dp.include_router(user_handlers.router)
    dp.include_router(other_handlers.router)

    # запускаем планировщик
    scheduler.start()

    # Пропускаем накопившиеся апдейты и запускаем polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    if hasattr(asyncio, 'WindowsSelectorEventLoopPolicy'):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    else:
        asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())
    asyncio.run(main())
