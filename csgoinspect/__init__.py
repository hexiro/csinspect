import logging
import pathlib

import dotenv
import rich.logging

logging.root.setLevel(logging.DEBUG)

# hacky way of setting all other loggers to ERROR
# there's probably a better way to do this.

for key in logging.Logger.manager.loggerDict:
    logging.getLogger(key).setLevel(logging.ERROR)

rich_handler = rich.logging.RichHandler(omit_repeated_times=True, rich_tracebacks=True)
rich_handler.setLevel(logging.DEBUG)

logging.root.addHandler(rich_handler)

dotenv_path = pathlib.Path(__file__).parents[1] / ".env"
dotenv.load_dotenv(dotenv_path)
