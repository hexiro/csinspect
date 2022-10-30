from __future__ import annotations

import sys
from datetime import datetime

import sentry_sdk
from loguru import logger

from csgoinspect.commons import IS_DEV, PARENT_DIRECTORY, SENTRY_DSN

if IS_DEV and SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        # We recommend adjusting this value in production.
        traces_sample_rate=1.0,
    )

LEVEL = "DEBUG" if IS_DEV else "INFO"

logs = PARENT_DIRECTORY / "logs"
logs.mkdir(exist_ok=True)

time_format = "<red>[{time:h:mm:ss A}]</red>"
level_format = "<level>{level: <8}</level>"

message_format = "<bold>{message}</bold>"
log_format = f"{time_format} {level_format} | {message_format}"

config = {
    "handlers": [
        {"sink": sys.stdout, "format": log_format, "level": LEVEL},
        {"sink": f"{logs}/{datetime.now():%Y-%m-%d}.log", "rotation": "1 day", "format": log_format, "level": "DEBUG"},
    ]
}
logger.configure(**config)  # type: ignore[arg-type]
