from dataclasses import dataclass
from environs import Env


@dataclass(slots=True, frozen=True)
class TgBot:
    token: str
    admin_ids: list[int]


@dataclass(slots=True, frozen=True)
class ConfigBot:
    tg_bot: TgBot


def load_config_bot(path: str | None = None) -> ConfigBot:
    env = Env()
    env.read_env(path)
    return ConfigBot(
        tg_bot=TgBot(
            token=env('BOT_TOKEN'),
            admin_ids=list(map(int, env.list('ADMIN_IDS')))
        )
    )


@dataclass(slots=True, frozen=True)
class DataBase:
    dsn: str
    is_echo: bool


@dataclass(slots=True, frozen=True)
class ConfigDB:
    database: DataBase


def load_config_db(path: str | None = None) -> ConfigDB:
    env = Env()
    env.read_env(path)
    return ConfigDB(
        database=DataBase(
            dsn=env('DSN'),
            is_echo=bool(env('IS_ECHO'))
        )
    )