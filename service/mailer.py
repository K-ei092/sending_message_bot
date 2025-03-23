import asyncio
import logging
import random
import time
from random import choice
from typing import Any

from aiogram import Bot
from aiogram.exceptions import TelegramRetryAfter, TelegramNetworkError
from aiogram.types import InlineKeyboardMarkup

from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlalchemy import Row, CursorResult

from bot import bot, db_engine
from database.worker import WorkerDB
from service.exercises import exercises_dict
from lexicon.lexicon import LEXICON, list_flower
from keyboards.kb import create_keyboar_recommendation_implemented


logger = logging.getLogger(__name__)


class Mailer(WorkerDB):
    def __init__(self, my_db_engine: AsyncEngine, user_id: int = 0):
        super().__init__(my_db_engine)
        self.bot: Bot = bot
        self.user_id: int = user_id

    async def send_exercise(self):
        user: Row[Any] = await self.check_before_send_exercise(self.user_id)
        if not user:
            return
        exercise_id: int = self._get_exercise_id(user)
        text: str = self._create_text_exercise(exercise_id)
        await self._send_message(text=text)
        if exercise_id > 0:
            await self.change_after_submitting_exercise(self.user_id, user.exercises_counter, user.completed_exercises,      # увеличиваем счетчик "30 заданий" на 1, добавляем к строке отправленных заданий новое
                                                        exercise_id, exercise_submission_status=True)                        # меняем состояние "задание отправлено" на - "да"
        if exercise_id == 0:
            await self.inflate_exercises_counter(self.user_id)                                                           # завышение счетчика "30 заданий" - уход от фильтра

    async def send_gratitude(self):
        user: Row[Any] = await self.check_before_send_gratitude(self.user_id)
        if not user:
            return
        my_keyboard: InlineKeyboardMarkup = create_keyboar_recommendation_implemented()
        text: str = self._create_text_gratitude()
        await self._send_message(text=text, reply_markup=my_keyboard)
        await self.change_exercise_state(self.user_id, False)                                                      # установлено состояние ожидание "лайка"
        await self.change_exercise_submission_status(self.user_id, False)                                          # меняем состояние "задание отправлено" на - "нет"
        if user.exercises_counter == 30:
            await asyncio.sleep(1)
            await self._send_message(text=LEXICON['last_task'])

    async def send_reminder(self):
        exercise_state: CursorResult = await self.get_state_exercise(self.user_id)
        state: bool = exercise_state.fetchall()[0][0]
        if state:
            return
        i = choice(range(len(LEXICON['reminder'])))
        await self._send_message(text=LEXICON['reminder'][i])

    async def send_statistic(self):
        statistics_text: str = await self.get_statistic(self.user_id)
        await self._send_message(text=statistics_text)

    async def _send_message(self, text: str, reply_markup: InlineKeyboardMarkup | None = None):
        try:
            time.sleep(0.025)
            await self.bot.send_message(chat_id=self.user_id, text=text, reply_markup=reply_markup, request_timeout=20)
        except TelegramRetryAfter as e:
            await asyncio.sleep(e.retry_after)
            await self.bot.send_message(chat_id=self.user_id, text=text, reply_markup=reply_markup, request_timeout=30)
        except TelegramNetworkError as e:
            if 'timeout error' in str(e):
                await asyncio.sleep(1)
                await self.bot.send_message(chat_id=self.user_id, text=text, reply_markup=reply_markup, request_timeout=30)
        except Exception as e:
            logger.error(f'Ошибка при рассылке ботом, пользователь {self.user_id}. Error: {e}', exc_info=True)

    @staticmethod
    def _create_text_exercise(exercise_id):
        exercise = exercises_dict.get(exercise_id, None)
        if exercise:
            text = LEXICON['exercise_text_1'].format(exercise=exercise)
            text += LEXICON['exercise_text_2_1'] \
                if exercise_id in (3, 10, 11, 12, 26, 27, 28, 29, 30, 35, 48, 50) \
                else LEXICON['exercise_text_2_2']
            return text
        return LEXICON['heppy_end']

    @staticmethod
    def _create_text_gratitude() -> str:
        i = choice(range(len(list_flower)))
        text: str = f'{list_flower[i]} {LEXICON["recommendation_implemented"]} {list_flower[i]}'
        return text

    @staticmethod
    def _get_exercise_id(user: Row) -> int:
        complited_exercises: set[int] = {int(i) for i in user.completed_exercises.split()}
        logger.info(complited_exercises)
        all_exercises: set[int] = set(range(1, len(exercises_dict) + 1))
        exercise_ids: list[int] = list(all_exercises.difference(complited_exercises))
        logger.info(exercise_ids)
        exercise_id: int = 0
        try:
            exercise_id = random.choice(exercise_ids)
            logger.info(exercise_id)
            return exercise_id
        except IndexError:
            logger.info(exercise_id)
            return exercise_id


async def send_exercise(user_id):
    mailer = Mailer(my_db_engine=db_engine, user_id=user_id)
    await mailer.send_exercise()

async def send_gratitude(user_id):
    mailer = Mailer(my_db_engine=db_engine, user_id=user_id)
    await mailer.send_gratitude()

async def send_reminder(user_id):
    mailer = Mailer(my_db_engine=db_engine, user_id=user_id)
    await mailer.send_reminder()


if __name__ == '__main__':
    send_exercise(1111)
    send_gratitude(1111)
    send_reminder(1111)
