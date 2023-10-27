from __future__ import annotations

import sys
from datetime import datetime

import sentry_sdk
from loguru import logger

from csinspect.config import LEVEL, DEV_MODE, LOGS_DIRECTORY, SENTRY_DSN, SENTRY_TRACES_SAMPLE_RATE

if not DEV_MODE and SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        traces_sample_rate=SENTRY_TRACES_SAMPLE_RATE,
    )

LOGS_DIRECTORY.mkdir(exist_ok=True)

# --- formats ---
TIME_FORMAT = "<red>[{time:h:mm:ss A}]</red>"
LEVEL_FORMAT = "<level>{level: <8}</level>"
MESSAGE_FORMAT = "<bold>{message}</bold>"
LOG_FORMAT = f"{TIME_FORMAT} {LEVEL_FORMAT} | {MESSAGE_FORMAT}"

CONFIG = {
    "handlers": [
        {"sink": sys.stdout, "format": LOG_FORMAT, "level": LEVEL},
        {"sink": f"{LOGS_DIRECTORY}/{datetime.now():%Y-%m-%d}.log", "rotation": "1 day", "format": LOG_FORMAT, "level": "DEBUG"},
    ]
}

logger.configure(**CONFIG)  # type: ignore[arg-type]
