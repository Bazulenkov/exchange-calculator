from logging.config import dictConfig
from pathlib import Path

from dotenv import load_dotenv
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).parent

DT_FORMAT = "%d.%m.%Y %H:%M:%S"

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "root": {
        "level": "DEBUG",
        "handlers": ["debug_console_handler", "rotating_file_handler"],
    },
    "handlers": {
        "debug_console_handler": {
            "level": "DEBUG",
            "formatter": "debug",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
        "rotating_file_handler": {
            "level": "INFO",
            "formatter": "info",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "info.log",
            "mode": "a",
            "maxBytes": 1048576,
            "backupCount": 5,
        },
    },
    "formatters": {
        "info": {
            "format": "%(asctime)s - [%(levelname)s] - %(message)s",
            "datefmt": DT_FORMAT,
        },
        "debug": {
            "format": (
                "%(asctime)s [%(levelname)s] - "
                "(%(filename)s).%(funcName)s:%(lineno)d - %(message)s"
            ),
            "datefmt": DT_FORMAT,
        },
    },
}


def configure_logging(filename: str = "info.log"):
    log_dir = BASE_DIR / "logs"
    log_dir.mkdir(exist_ok=True)
    filename = Path(filename).with_suffix(".log")
    LOGGING_CONFIG["handlers"]["rotating_file_handler"]["filename"] = log_dir / filename
    dictConfig(LOGGING_CONFIG)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8" , extra="ignore"
    )
    tg_bot_token: SecretStr


load_dotenv()

config = Settings()
