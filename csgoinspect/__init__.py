from __future__ import annotations

import pathlib
import sys
from datetime import datetime

import dotenv
from loguru import logger

parent_directory = pathlib.Path(__file__).parents[1]
dotenv_path = parent_directory / ".env"
dotenv.load_dotenv(dotenv_path)

logs = parent_directory / "logs"
logs.mkdir(exist_ok=True)

time_format = "<red>[{time:MM-DD-YY h:mm:ss A}]</red>"
level_format = "<level>{level: <8}</level>"
name_format = "<cyan>{name}</cyan>"
line_format = "<blue>{line}</blue>"
message_format = "<bold>{message}</bold>"
log_format = f"{time_format} {level_format}| {name_format}:{line_format} | {message_format}"

config = {
    "handlers": [
        {"sink": sys.stdout, "format": log_format, "level": "DEBUG"},
        {"sink": f"{logs}/{datetime.now():%Y-%m-%d}.log", "rotation": "1 day", "format": log_format, "level": "DEBUG"}
    ]
}
logger.configure(**config)
