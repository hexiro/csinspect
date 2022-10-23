from __future__ import annotations

import asyncio

from csgoinspect.csgoinspect import CSGOInspect


async def main() -> None:
    csgo_inspect = CSGOInspect()
    await csgo_inspect.run()


if __name__ == "__main__":
    asyncio.run(main())
