from __future__ import annotations

import asyncio
import json
import typing as t

import httpx
import socketio
from loguru import logger

if t.TYPE_CHECKING:
    from csinspect.item import Item
    from csinspect.typings import SwapGGScreenshotReady, SwapGGScreenshotResponse, SwapGGScreenshotResult


class Screenshot:
    USER_AGENT = "csinspect; (+https://github.com/hexiro/csinspect)"
    SWAPGG_API_HEADERS: t.ClassVar = {
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://swap.gg/",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "User-Agent": USER_AGENT,
    }
    SWAP_GG_WS_HEADERS: t.ClassVar = {
        "User-Agent": USER_AGENT,
    }

    def __init__(self: Screenshot) -> None:
        self.swap_gg_socket = socketio.AsyncClient(handle_sigint=True)
        self.screenshot_queue: set[str] = set()  # set[image_id]

        async def on_connect() -> None:
            logger.debug("CONNECTED: swap.gg WebSocket")

        async def on_disconnect() -> None:
            logger.warning("DISCONNECTED: swap.gg WebSocket")
            await self.connect_websocket()

        self.swap_gg_socket.on("connect", on_connect)
        self.swap_gg_socket.on("disconnect", on_disconnect)
        self.swap_gg_socket.on("screenshot:ready", self.on_swap_gg_screenshot)

    async def connect_websocket(self: Screenshot) -> None:
        if self.swap_gg_socket.connected:
            return

        await self.swap_gg_socket.connect(url="https://ws.swap.gg", headers=self.SWAP_GG_WS_HEADERS)

    async def on_swap_gg_screenshot(self: Screenshot, data: SwapGGScreenshotReady) -> None:
        image_id = data["imageId"]

        if image_id not in self.screenshot_queue:
            logger.debug(f"SCREENSHOT NOT IN QUEUE: {image_id}")
            return

        logger.debug(f"SCREENSHOT READY: {image_id}")
        self.screenshot_queue.remove(image_id)

    async def swap_gg_screenshot(self: Screenshot, item: Item) -> bool:
        try:
            async with httpx.AsyncClient() as session:
                payload = {"inspectLink": item.unquoted_inspect_link}
                response = await session.post(
                    url="https://api.swap.gg/v2/screenshot",
                    headers=self.SWAPGG_API_HEADERS,
                    json=payload,
                )
            data: SwapGGScreenshotResponse = response.json()
        except httpx.HTTPError:
            logger.exception(f"SWAP.GG SCREENSHOT FAILED (HTTP ERROR: {item.inspect_link})")
            return False
        except json.JSONDecodeError:
            logger.exception(f"SWAP.GG SCREENSHOT FAILED (JSON DECODE ERROR: {item.inspect_link})")
            return False

        logger.debug(f"SWAP.GG SCREENSHOT RESPONSE: {data}")

        if data["status"] != "OK":
            logger.debug(f"SWAP.GG SCREENSHOT FAILED (Not Ok): {data}")
            return False

        try:
            result: SwapGGScreenshotResult = data["result"]  # type: ignore[assignment, typeddict-item]
        except KeyError:
            logger.debug(f"SWAP.GG SCREENSHOT FAILED (No Result): {data}")
            return False

        image_id = result["imageId"]
        item.image_id = image_id

        if result["state"] == "COMPLETED":
            return True

        self.screenshot_queue.add(image_id)

        logger.debug(f"SCREENSHOT QUEUED: {item.inspect_link}")
        logger.debug(f"SCREENSHOT QUEUE: {self.screenshot_queue}")
        logger.debug(f"ITEM IN QUEUE: {item in self.screenshot_queue}")

        while image_id in self.screenshot_queue:
            logger.debug(f"SCREENSHOT WAITING: {item.inspect_link}")
            await asyncio.sleep(1)

        return True

    async def screenshot_item(self: Screenshot, item: Item) -> bool:
        logger.debug(f"SCREENSHOTTING: {item.inspect_link}")

        swapgg_success = await self.swap_gg_screenshot(item)

        if not swapgg_success or not item.image_id:
            logger.warning(f"SCREENSHOT FAILED: {item.inspect_link}")
            return False

        logger.debug(f"SCREENSHOT COMPLETE: {item.image_link} {swapgg_success=}")
        return True

    async def screenshot_items(self: Screenshot, items: t.Iterable[Item]) -> list[bool]:
        screenshot_tasks: list[asyncio.Task[bool]] = []

        for item in items:
            screenshot_coro = self.screenshot_item(item)
            screenshot_task = asyncio.create_task(screenshot_coro)
            screenshot_tasks.append(screenshot_task)

        screenshot_responses: list[bool] = await asyncio.gather(*screenshot_tasks)
        return screenshot_responses
