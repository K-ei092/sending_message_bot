from sqlalchemy import Table, MetaData, Column, BigInteger, Integer, String, DateTime, Boolean
from datetime import datetime


metadata = MetaData()

users = Table(
    "users",
    metadata,
    Column("telegram_id", BigInteger, primary_key=True),
    Column("telegram_name", String),
    Column("first_name", String),
    Column("last_name", String),
    Column("exercises_counter", Integer, default=0),                        # счетчик 30 отправленных заданий
    Column("completed_exercises", String, default=' '),                     # строка отправленных заданий
    Column('created_on', DateTime(), default=datetime.now),
    Column('exercise_state', Boolean, default=True),                        # True - задание выполнено "лайк" / False - ожидание лайка
    Column("record_counter", Integer, default=0),                           # сколько всего заданий выполнено
    Column('exercise_submission_status', Boolean, default=False)            # задание не отправлено / да
)



