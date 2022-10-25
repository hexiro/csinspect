from __future__ import annotations

import asyncio
import typing as t

import httpx
import socketio
from loguru import logger

if t.TYPE_CHECKING:
    from csgoinspect.item import Item
    from csgoinspect.tweet import TweetWithItems
    from csgoinspect.typings import ScreenshotReady, SwapGGScreenshotResponse


class SwapGG:
    HEADERS = {
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://market.swap.gg/",
        "Referrer-Policy": "strict-origin-when-cross-origin",
    }

    def __init__(self) -> None:
        self.socket = socketio.AsyncClient(handle_sigint=True)
        self.screenshot_queue: list[Item] = []

        async def on_connect() -> None:
            logger.debug("CONNECTING: swap.gg WebSocket")

        async def on_disconnect() -> None:
            logger.warning("DISCONNECTING: swap.gg WebSocket")

        self.socket.on("connect", on_connect)
        self.socket.on("disconnect", on_disconnect)
        self.socket.on("screenshot:ready", self.on_screenshot)

    async def on_screenshot(self, data: ScreenshotReady) -> None:
        def find_item(unquoted_inspect_link: str) -> Item | None:
            for item in self.screenshot_queue:
                if item.unquoted_inspect_link == unquoted_inspect_link:
                    return item
            return None

        unquoted_inspect_link = data["inspectLink"]
        image_link = data["imageLink"]

        if item := find_item(unquoted_inspect_link):

            item.image_link = image_link
            item.is_ready = True

            self.screenshot_queue.remove(item)

            return

    async def connect(self) -> None:
        if self.socket.connected:
            return
        await self.socket.connect("wss://market-ws.swap.gg")

    async def disconnect(self) -> None:
        if not self.socket.connected:
            return
        await self.socket.disconnect()

    async def screenshot(self, item: Item) -> None:
        payload = {"inspectLink": item.unquoted_inspect_link}

        logger.debug(f"SCREENSHOTTING: {item.inspect_link}")

        try:
            async with httpx.AsyncClient() as session:
                response = await session.post(
                    "https://market-api.swap.gg/v1/screenshot", headers=self.HEADERS, json=payload
                )
            data: SwapGGScreenshotResponse = response.json()
        except httpx.HTTPError:
            return

        if data["status"] != "OK":
            item.is_ready = True

            return
        if data["result"]["state"] == "COMPLETED":
            item.image_link = data["result"]["imageLink"]  # type: ignore
            item.is_ready = True

            return

        await self.connect()
        self.screenshot_queue.append(item)

        while not item.is_ready:
            await asyncio.sleep(1)

    async def screenshot_tweet(self, tweet: TweetWithItems) -> None:

        screenshot_tasks: list[asyncio.Task[None]] = []
        for item in tweet.items:
            screenshot_coro = self.screenshot(item)
            screenshot_task = asyncio.create_task(screenshot_coro)
            screenshot_tasks.append(screenshot_task)

        await asyncio.gather(*screenshot_tasks)
