from __future__ import annotations

import logging
import pathlib

import dotenv
from rich.console import Console
from rich.logging import RichHandler

console = Console(force_terminal=True, color_system="truecolor", width=260)
rich_handler = RichHandler(console=console, omit_repeated_times=False)

logging.basicConfig(
    level=logging.DEBUG,
    format="%(name)s %(message)s",
    datefmt="[%X]",
    handlers=[rich_handler]
)

# hacky way of setting other loggers to CRITICAL
# there's probably a better way to handle other loggers

logging.getLogger("tweepy").setLevel(logging.CRITICAL)
logging.getLogger("urllib3").setLevel(logging.CRITICAL)
logging.getLogger("requests_oauthlib").setLevel(logging.CRITICAL)
logging.getLogger("oauthlib").setLevel(logging.CRITICAL)

dotenv_path = pathlib.Path(__file__).parents[1] / ".env"
dotenv.load_dotenv(dotenv_path)
