from __future__ import annotations

import asyncio

from loguru import logger

from csinspect.csinspect import CSInspect


async def main() -> None:
    try:
        cs_inspect = CSInspect()
        await cs_inspect.run()
    except Exception:
        logger.exception("Error Running CSInspect")


if __name__ == "__main__":
    asyncio.run(main())
