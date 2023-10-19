from __future__ import annotations

import asyncio
import typing as t

import httpx
import socketio
from loguru import logger

if t.TYPE_CHECKING:
    from csinspect.item import Item
    from csinspect.tweet import TweetWithItems
    from csinspect.typings import SwapGGScreenshotReady, SwapGGScreenshotResponse, SwapGGScreenshotResult


class ScreenshotTools:
    SWAPGG_HEADERS = {
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://market.swap.gg/",
        "Referrer-Policy": "strict-origin-when-cross-origin",
    }

    def __init__(self: ScreenshotTools) -> None:
        self.swap_gg_socket = socketio.AsyncClient(handle_sigint=True)
        self.screenshot_queue: set[Item] = set()

        async def on_connect() -> None:
            logger.debug("CONNECTED: swap.gg WebSocket")

        async def on_disconnect() -> None:
            logger.warning("DISCONNECTED: swap.gg WebSocket")

        self.swap_gg_socket.on("connect", on_connect)
        self.swap_gg_socket.on("disconnect", on_disconnect)
        self.swap_gg_socket.on("screenshot:ready", self.on_swap_gg_screenshot)

    async def on_swap_gg_screenshot(self: ScreenshotTools, data: SwapGGScreenshotReady) -> None:
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

    async def screenshot(self: ScreenshotTools, item: Item) -> bool:
        # sourcery skip: assign-if-exp, introduce-default-else, move-assign-in-block, swap-if-expression
        logger.debug(f"SCREENSHOTTING: {item.inspect_link}")

        swapgg_success: bool = False
        swapgg_success = await self._swap_gg_screenshot(item)

        if not swapgg_success or not item.image_link:
            logger.warning(f"SCREENSHOT FAILED: {item.inspect_link}")
            return False

        logger.debug(f"SCREENSHOT COMPLETE: {item.image_link} {swapgg_success=}")
        return True

    async def _swap_gg_screenshot(self: ScreenshotTools, item: Item) -> bool:
        payload = {"inspectLink": item.unquoted_inspect_link}

        try:
            async with httpx.AsyncClient() as session:
                response = await session.post(
                    "https://market-api.swap.gg/v1/screenshot", headers=self.SWAPGG_HEADERS, json=payload
                )
            data: SwapGGScreenshotResponse = response.json()
        except httpx.HTTPError:
            logger.exception(f"SWAP.GG SCREENSHOT FAILED (HTTP ERROR: {item.inspect_link})")
            return False

        if data["status"] != "OK":
            logger.debug(f"SWAP.GG SCREENSHOT FAILED (Not Ok): {data}")
            return False

        result: SwapGGScreenshotResult | None = data.get("result")  # type: ignore[assignment]

        if not result:
            logger.debug(f"SWAP.GG SCREENSHOT FAILED (No Result): {data}")
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

    async def screenshot_tweet(
        self: ScreenshotTools, tweet: TweetWithItems
    ) -> list[bool]:
        screenshot_tasks: list[asyncio.Task[bool]] = []

        for item in tweet.items:
            screenshot_coro = self.screenshot(item)
            screenshot_task = asyncio.create_task(screenshot_coro)
            screenshot_tasks.append(screenshot_task)

        screenshot_responses: list[bool] = await asyncio.gather(*screenshot_tasks)
        return screenshot_responses
