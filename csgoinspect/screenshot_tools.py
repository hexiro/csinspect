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
        self.screenshot_queue: list[Item] = []

        async def on_connect() -> None:
            logger.debug("CONNECTING: swap.gg WebSocket")

        async def on_disconnect() -> None:
            logger.warning("DISCONNECTING: swap.gg WebSocket")

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
            item.is_ready = True

            self.screenshot_queue.remove(item)

            return

        logger.debug(f"SCREENSHOT RECEIVED : {unquoted_inspect_link}")

    async def screenshot(self, item: Item) -> None:
        if swap_gg_screenshot := await self._swap_gg_screenshot(item):
            item.image_link = swap_gg_screenshot
            item.is_ready = True
            return
        logger.warning(f"SWAP.GG SCREENSHOT FAILED: {item.inspect_link}")
        if skinport_screenshot := await self._skinport_screenshot(item):
            item.image_link = skinport_screenshot
            item.is_ready = True
            return
        logger.warning(f"SKINPORT SCREENSHOT FAILED: {item.inspect_link}")

    async def _swap_gg_screenshot(self, item: Item) -> str | None:
        payload = {"inspectLink": item.unquoted_inspect_link}

        logger.debug(f"SCREENSHOTTING: {item.inspect_link}")

        try:
            async with httpx.AsyncClient() as session:
                response = await session.post(
                    "https://market-api.swap.gg/v1/screenshot", headers=self.SWAPGG_HEADERS, json=payload
                )
            data: SwapGGScreenshotResponse = response.json()
        except httpx.HTTPError:
            return None

        if data["status"] != "OK":
            return None

        result: SwapGGScreenshotResult | None = data.get("result")  # type: ignore[assignment]

        if not result:
            return None

        if result["state"] == "COMPLETED":
            return data["result"]["imageLink"]  # type: ignore

        if not self.swap_gg_socket.connected:
            await self.swap_gg_socket.connect("wss://market-ws.swap.gg")

        self.screenshot_queue.append(item)

        while not item.is_ready:
            await asyncio.sleep(1)

        return None

    async def _skinport_screenshot(self, item: Item) -> str | None:
        """
        Unlike swap.gg, Skinport does not use a WebSocket connection to get the screenshot.
        """
        async with httpx.AsyncClient(timeout=120, follow_redirects=False) as session:
            params = {"link": item.unquoted_inspect_link}
            response = await session.get("https://screenshot.skinport.com/direct", params=params)

            if response.status_code == 308 and response.next_request:  # redirects and format inspect link
                response = await session.send(response.next_request)

            if response.status_code == 307 and response.next_request:
                return str(response.next_request.url)

        if response.next_request:
            item.inspect_link = str(response.next_request.url)
            item.is_ready = True

        return None

    async def screenshot_tweet(self, tweet: TweetWithItems) -> None:

        screenshot_tasks: list[asyncio.Task[None]] = []
        for item in tweet.items:
            screenshot_coro = self.screenshot(item)
            screenshot_task = asyncio.create_task(screenshot_coro)
            screenshot_tasks.append(screenshot_task)

        await asyncio.gather(*screenshot_tasks)
