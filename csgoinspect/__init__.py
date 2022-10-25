from __future__ import annotations

import os
import pathlib
import sys
from datetime import datetime

import dotenv
import sentry_sdk
from loguru import logger

parent_directory = pathlib.Path(__file__).parents[1]
dotenv_path = parent_directory / ".env"
if dotenv_path.is_file():
    dotenv.load_dotenv(dotenv_path)


SENTRY_DSN = os.getenv("SENTRY_DSN")
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        # We recommend adjusting this value in production.
        traces_sample_rate=1.0,
    )


logs = parent_directory / "logs"
logs.mkdir(exist_ok=True)

time_format = "<red>[{time:h:mm:ss A}]</red>"
level_format = "<level>{level: <6}</level>"

message_format = "<bold>{message}</bold>"
log_format = f"{time_format} {level_format} | {message_format}"

config = {
    "handlers": [
        {"sink": sys.stdout, "format": log_format, "level": "DEBUG"},
        {"sink": f"{logs}/{datetime.now():%Y-%m-%d}.log", "rotation": "1 day", "format": log_format, "level": "DEBUG"},
    ]
}
logger.configure(**config)  # type: ignore[arg-type]
