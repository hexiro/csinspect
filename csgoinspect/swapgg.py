from __future__ import annotations

import logging
from enum import Enum, auto
from typing import TYPE_CHECKING, Optional

import requests
import socketio

if TYPE_CHECKING:
    from csgoinspect.typings import SwapGGScreenshotResponse, ScreenshotReady
    from csgoinspect.item import Item

logger = logging.getLogger(__name__)


class ScreenshotState(Enum):
    INVALID = auto()
    WAITING = auto()
    COMPLETE = auto()


class SwapGG:
    headers = {
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://market.swap.gg/",
        "Referrer-Policy": "strict-origin-when-cross-origin",
    }
    screenshots: dict[Item, ScreenshotState] = {}

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __init__(self):
        self.socket = socketio.Client(handle_sigint=True)
        self.socket.connect("wss://market-ws.swap.gg")

        @self.socket.on("connect")
        def on_connect():
            self.on_connect()

        @self.socket.on("screenshot:ready")
        def on_screenshot(data: ScreenshotReady):
            self.on_screenshot(data)

    @staticmethod
    def on_connect():
        logger.debug("connected to swap.gg socket.io websocket")

    def on_screenshot(self, data: ScreenshotReady):
        # logger.debug(f"SCREENSHOT:READY {data}")

        unquoted_inspect_link = data["inspectLink"]
        image_link = data["imageLink"]

        if item := self.find_item(unquoted_inspect_link):
            logger.debug(f"screenshot:ready for item: {item}")
            logger.debug(f"saved image link for item: {item}")
            item.image_link = image_link
        else:
            logger.debug(f"can't find item with inspect_link: {unquoted_inspect_link}")

    def find_item(self, unquoted_inspect_link: str) -> Optional[Item]:
        for item in self.screenshots:
            if item.unquoted_inspect_link == unquoted_inspect_link:
                return item
        return None

    def screenshot(self, item: Item) -> None:
        payload = {
            "inspectLink": item.unquoted_inspect_link
        }

        logger.debug(f"requesting screenshot for item: {item}")
        logging.debug(f"payload: {payload}")

        try:
            response = requests.post("https://market-api.swap.gg/v1/screenshot", headers=self.headers, json=payload)
            data: SwapGGScreenshotResponse = response.json()
        except requests.RequestException:
            logger.warning(f"Failed to receive response for item: {item}")
            self.screenshots[item] = ScreenshotState.INVALID
            return

        if data["status"] != "OK":
            logging.warning(f"Failed to request screenshot for item: {item}")
            self.screenshots[item] = ScreenshotState.INVALID
        elif data["result"]["state"] == "COMPLETED":
            logger.debug(f"screenshot already taken for item: {item}")
            item.image_link = data["result"]["imageLink"]
            self.screenshots[item] = ScreenshotState.COMPLETE
        else:
            logger.debug(f"screenshotting -- inspect link: {item.unquoted_inspect_link}")
            self.screenshots[item] = ScreenshotState.WAITING

    def close(self):
        self.socket.disconnect()
