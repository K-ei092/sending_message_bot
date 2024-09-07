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
    Column("exercises_counter", Integer, default=0),
    Column("completed_exercises", String, default=' '),
    Column('created_on', DateTime(), default=datetime.now),
    Column('exercise_state', Boolean, default=True),
    Column("record_counter", Integer, default=0),
    Column('exercise_submission_status', Boolean, default=False)
)



