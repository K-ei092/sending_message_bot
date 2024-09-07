import asyncio
import logging
import time
from random import choice, randint

from aiogram import Bot
from aiogram.exceptions import TelegramRetryAfter, TelegramNetworkError
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlalchemy import select

from database.table_processing import (
    change_exercise_state,
    get_false_state_exercise,
    get_all_user_id,
    get_statistic, get_state_exercise
)

from database.tables import users as users_table
from service.exercises import exercises_dict

from lexicon.lexicon import LEXICON, list_flower
from keyboards.kb import create_keyboar_recommendation_implemented


logger = logging.getLogger(__name__)


async def send_exercise(bot: Bot, db_engine: AsyncEngine, user_id: int = 0):

    if user_id == 0:
        stmt = select("*").select_from(users_table)
    else:
        stmt = select("*").where(users_table.c.telegram_id == user_id)

    async with db_engine.connect() as conn:

        users = await conn.execute(stmt)

        for user in users:

            if user.exercises_counter < 30:

                comp_ex = [int(i) for i in user.completed_exercises.split()]
                while True:
                    exercise_id = randint(1, len(exercises_dict))
                    if (exercise_id not in comp_ex) \
                            or (len(comp_ex) == len(exercises_dict)):
                        break

                if user.exercise_state and not user.exercise_submission_status:

                    text = f'<u>Сегодня по плану:</u>\n\n' \
                           f'🟢 <b>{exercises_dict[exercise_id]}</b>\n\n'

                    try:
                        time.sleep(0.025)
                        await bot.send_message(chat_id=user.telegram_id, text=text, request_timeout=30)

                    except TelegramRetryAfter as e:
                        retry_after = e.retry_after
                        await asyncio.sleep(retry_after)
                        await bot.send_message(chat_id=user.telegram_id, text=text, request_timeout=30)

                    except TelegramNetworkError as e:
                        if 'timeout error' in str(e):
                            await asyncio.sleep(1)
                            await bot.send_message(chat_id=user.telegram_id, text=text, request_timeout=30)

                    except Exception:
                        logger.error(f'Ошибка при рассылке задания, пользователь {user.telegram_id}',
                                     exc_info=True)

                    await conn.execute(
                        users_table.update().where(users_table.c.telegram_id == user.telegram_id)
                        .values(exercises_counter=user.exercises_counter + 1,
                                completed_exercises=user.completed_exercises + ' ' + str(exercise_id),
                                exercise_submission_status=True)
                    )

                    await conn.commit()

                if len(user.completed_exercises.split()) == len(exercises_dict):

                    await conn.execute(
                        users_table.update().where(users_table.c.telegram_id == user.telegram_id)
                        .values(exercises_counter=31)
                    )

                    await conn.commit()

                    try:
                        await bot.send_message(user.telegram_id, LEXICON['heppy_end'], request_timeout=30)

                    except Exception:
                        logger.error(
                            f'Ошибка при отправке сообщения об окончании всех заданий, '
                            f'пользователь {user.telegram_id}',
                            exc_info=True
                        )


async def send_self_gratitude(bot: Bot, db_engine: AsyncEngine, user_id: int = 0):

    if user_id == 0:
        stmt = select("*").select_from(users_table)
    else:
        stmt = select("*").where(users_table.c.telegram_id == user_id)

    async with db_engine.connect() as conn:
        users = await conn.execute(stmt)

        for user in users:

            if user.exercises_counter < 31:

                if user.exercise_state and user.exercise_submission_status:

                    time.sleep(0.025)
                    my_keyboard = create_keyboar_recommendation_implemented()
                    i = choice(range(len(list_flower)))
                    text = f'{list_flower[i]} {LEXICON["recommendation_implemented"]} {list_flower[i]}'

                    try:
                        await bot.send_message(chat_id=user.telegram_id, text=text,
                                               reply_markup=my_keyboard, request_timeout=30)

                    except TelegramRetryAfter as e:
                        retry_after = e.retry_after
                        await asyncio.sleep(retry_after)
                        await bot.send_message(chat_id=user.telegram_id, text=text,
                                               reply_markup=my_keyboard, request_timeout=30)

                    except TelegramNetworkError as e:
                        if 'timeout error' in str(e):
                            await asyncio.sleep(1)
                            await bot.send_message(chat_id=user.telegram_id, text=text,
                                                   reply_markup=my_keyboard, request_timeout=30)

                    except Exception:
                        logger.error(
                            f'Ошибка при рассылке напоминания о благодарности, '
                            f'пользователь {user.telegram_id}',
                            exc_info=True
                        )

                    await change_exercise_state(db_engine, user.telegram_id, False)

                    if user.exercises_counter == 30:
                        await asyncio.sleep(1)
                        try:
                            await bot.send_message(chat_id=user.telegram_id, text=LEXICON['last_task'],
                                                   request_timeout=30)
                        except Exception:
                            logger.error(
                                f'Ошибка при отправке сообщения о последнем задании в блоке, '
                                f'пользователь {user.telegram_id}',
                                exc_info=True
                            )

                    await conn.execute(
                        users_table.update().where(users_table.c.telegram_id == user.telegram_id)
                        .values(exercise_submission_status=False)
                    )
                    await conn.commit()


async def send_reminder(bot: Bot, db_engine: AsyncEngine, user_id: int = 0):

    if user_id == 0:
        users_id = await get_false_state_exercise(db_engine)
    else:
        state_ex = await get_state_exercise(db_engine, user_id)
        res = state_ex.fetchall()[0][0]
        if res:
            return
        users_id = [[user_id]]

    for user_id in users_id:

        i = choice(range(len(LEXICON['reminder'])))

        try:
            time.sleep(0.025)
            await bot.send_message(chat_id=user_id[0], text=LEXICON['reminder'][i], request_timeout=20)

        except TelegramRetryAfter as e:
            retry_after = e.retry_after
            await asyncio.sleep(retry_after)
            await bot.send_message(chat_id=user_id[0], text=LEXICON['reminder'][i], request_timeout=20)

        except TelegramNetworkError as e:
            if 'timeout error' in str(e):
                await asyncio.sleep(1)
                await bot.send_message(chat_id=user_id[0], text=LEXICON['reminder'][i], request_timeout=20)

        except Exception:
            logger.error(
                f'Ошибка при отправке напоминания о нажатии лайка, '
                f'пользователь {user_id[0]}',
                exc_info=True
            )


async def send_statistic(bot: Bot, db_engine: AsyncEngine, user_id: int = 0):

    if user_id == 0:
        list_users_id = await get_all_user_id(db_engine)
    else:
        list_users_id = [user_id]

    for user_id in list_users_id:

        statistics_text = await get_statistic(db_engine, user_id)

        try:
            time.sleep(0.025)
            await bot.send_message(chat_id=user_id, text=statistics_text, request_timeout=20)

        except TelegramRetryAfter as e:
            retry_after = e.retry_after
            await asyncio.sleep(retry_after)
            await bot.send_message(chat_id=user_id, text=statistics_text, request_timeout=20)

        except TelegramNetworkError as e:
            if 'timeout error' in str(e):
                await asyncio.sleep(1)
                await bot.send_message(chat_id=user_id, text=statistics_text, request_timeout=20)

        except Exception:
            logger.error(
                f'Ошибка при отправке статистики, '
                f'пользователь {user_id}',
                exc_info=True
            )
