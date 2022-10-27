from __future__ import annotations

import asyncio
import typing as t

import httpx
import socketio
from loguru import logger

if t.TYPE_CHECKING:
    from csgoinspect.item import Item
    from csgoinspect.tweet import TweetWithItems
    from csgoinspect.typings import SwapGGScreenshotReady, SwapGGScreenshotResponse, SwapGGScreenshotResult


class ScreenshotTools:
    SWAPGG_HEADERS = {
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://market.swap.gg/",
        "Referrer-Policy": "strict-origin-when-cross-origin",
    }

    def __init__(self) -> None:
        self.swap_gg_socket = socketio.AsyncClient(handle_sigint=True)
        self.screenshot_queue: set[Item] = set()

        async def on_connect() -> None:
            logger.debug("CONNECTED: swap.gg WebSocket")

        async def on_disconnect() -> None:
            logger.warning("DISCONNECTED: swap.gg WebSocket")

        self.swap_gg_socket.on("connect", on_connect)
        self.swap_gg_socket.on("disconnect", on_disconnect)
        self.swap_gg_socket.on("screenshot:ready", self.on_swap_gg_screenshot)

    async def on_swap_gg_screenshot(self, data: SwapGGScreenshotReady) -> None:
        def find_item(unquoted_inspect_link: str) -> Item | None:
            for item in self.screenshot_queue:
                if item.unquoted_inspect_link == unquoted_inspect_link:
                    return item
            return None

        unquoted_inspect_link = data["inspectLink"]
        image_link = data["imageLink"]

        if item := find_item(unquoted_inspect_link):

            logger.debug(f"SCREENSHOT READY: {item.inspect_link}")

            item.image_link = image_link
            self.screenshot_queue.remove(item)

            return

        logger.debug(f"SCREENSHOT RECEIVED : {unquoted_inspect_link}")

    async def screenshot(self, item: Item) -> bool:
        logger.debug(f"SCREENSHOTTING: {item.inspect_link}")

        if not await self._swap_gg_screenshot(item):
            logger.warning(f"SWAP.GG SCREENSHOT FAILED: {item.inspect_link}")
        elif not await self._skinport_screenshot(item):
            logger.warning(f"SKINPORT SCREENSHOT FAILED: {item.inspect_link}")
        else:
            return False

        logger.debug(f"SCREENSHOT COMPLETE: {item.image_link}")
        return True

    async def _swap_gg_screenshot(self, item: Item) -> bool:
        payload = {"inspectLink": item.unquoted_inspect_link}

        try:
            async with httpx.AsyncClient() as session:
                response = await session.post(
                    "https://market-api.swap.gg/v1/screenshot", headers=self.SWAPGG_HEADERS, json=payload
                )
            data: SwapGGScreenshotResponse = response.json()
        except httpx.HTTPError:
            return False

        if data["status"] != "OK":
            return False

        result: SwapGGScreenshotResult | None = data.get("result")  # type: ignore[assignment]

        if not result:
            return False

        if result["state"] == "COMPLETED":
            image_link: str = data["result"]["imageLink"]  # type: ignore
            item.image_link = image_link
            return True

        if not self.swap_gg_socket.connected:
            await self.swap_gg_socket.connect("wss://market-ws.swap.gg")

        self.screenshot_queue.add(item)

        logger.debug(f"SCREENSHOT QUEUED: {item.inspect_link}")
        logger.debug(f"SCREENSHOT QUEUE: {self.screenshot_queue}")

        logger.debug(f"ITEM IN QUEUE: {item in self.screenshot_queue}")

        while item in self.screenshot_queue:
            logger.debug(f"SCREENSHOT WAITING: {item.inspect_link}")
            await asyncio.sleep(1)

        return True

    async def _skinport_screenshot(self, item: Item) -> bool:
        """
        Unlike swap.gg, Skinport does not use a WebSocket connection to get the screenshot.
        """
        async with httpx.AsyncClient(timeout=120, follow_redirects=False) as session:
            params = {"link": item.unquoted_inspect_link}
            response = await session.get("https://screenshot.skinport.com/direct", params=params)

            if response.status_code == 308 and response.next_request:  # redirects and format inspect link
                response = await session.send(response.next_request)

        if response.next_request:
            item.inspect_link = str(response.next_request.url)
            return True

        return False

    async def screenshot_tweet(self, tweet: TweetWithItems) -> list[bool]:
        screenshot_tasks: list[asyncio.Task[bool]] = []
        for item in tweet.items:
            screenshot_coro = self.screenshot(item)
            screenshot_task = asyncio.create_task(screenshot_coro)
            screenshot_tasks.append(screenshot_task)

        screenshot_responses: list[bool] = await asyncio.gather(*screenshot_tasks)
        return screenshot_responses
