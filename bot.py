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


# Загружаем конфиг
config_bot: ConfigBot = load_config_bot()
config_db: ConfigDB = load_config_db()

# инициализируем бот и соединение СУБД
bot = Bot(token=config_bot.tg_bot.token, default=DefaultBotProperties(parse_mode='HTML'))          # 'MarkdownV2'
db_engine = create_async_engine(url=config_db.database.dsn, echo=config_db.database.is_echo,
                                pool_size=15, max_overflow=-1, pool_timeout=45)


# Функция конфигурирования и запуска бота
async def main(mybot, my_db_engine):

    logging.basicConfig(
        level=logging.WARNING,                                 # настройка - DEBUG, production - WARNING
        filename="logs.log",                               # добавляем логи в файл
        filemode='w',                                      # режим записи (a - добавить, w - переписать)
        format='%(filename)s:%(lineno)d #%(levelname)-8s '
               '[%(asctime)s] - %(name)s - %(message)s')
    logger.info('Starting bot')

    # инициализируем создание таблицы
    async with my_db_engine.begin() as conn:
        # await conn.run_sync(metadata.drop_all)
        await conn.run_sync(metadata.create_all)

    # Инициализируем хранилище для FSM
    if os.name == 'nt':
        storage = MemoryStorage()
    else:
        aio_redis = Redis(host='localhost')
        storage = RedisStorage(redis=aio_redis)

    # Настраиваем бот
    await set_main_menu(mybot)

    # настраиваем хранилище для тасков
    job_stores = {
        'default': RedisJobStore()
    }

    # job_stores = {
    #     "default": RedisJobStore(
    #         jobs_key="dispatched_trips_jobs", run_times_key="dispatched_trips_running"
    #         # параметры host и port необязательны, для примера показано как передавать параметры подключения
    #         # host="localhost", port=6379
    #     )
    # }
    # # Инициализируем планировщик задач
    # scheduler = AsyncIOScheduler(jobstores=job_stores)

    # Оборачиваем AsyncIOScheduler специальным классом
    scheduler = ContextSchedulerDecorator(AsyncIOScheduler(jobstores=job_stores))

    # Добавляем зависимости таска в некий контекст
    scheduler.ctx.add_instance(mybot, declared_class=Bot)
    scheduler.ctx.add_instance(my_db_engine, declared_class=AsyncEngine)

    dp = Dispatcher(storage=storage, db_engine=my_db_engine, scheduler=scheduler)
    dp.include_router(admin_handlers.router)
    dp.include_router(user_handlers.router)
    dp.include_router(other_handlers.router)

    scheduler.start()

    await mybot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(mybot)


if __name__ == '__main__':
    if hasattr(asyncio, 'WindowsSelectorEventLoopPolicy'):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    else:
        asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())
    asyncio.run(main(mybot=bot, my_db_engine=db_engine))
