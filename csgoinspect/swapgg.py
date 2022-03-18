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
        self.socket = socketio.Client()
        self.socket.connect("wss://market-ws.swap.gg")

        @self.socket.on("connect")
        def on_connect():
            logger.debug("connected to swap.gg socket.io websocket")

        @self.socket.on("screenshot:ready")
        def on_message(data: ScreenshotReady):
            logger.debug(f"SCREENSHOT:READY {data}")

            unquoted_inspect_link = data["inspectLink"]
            item = self.find_item(unquoted_inspect_link)

            if item:
                logger.debug("screenshot data saved!")
                item.image_link = data["imageLink"]

    def find_item(self, unquoted_inspect_link: str) -> Optional[Item]:
        for item in self.screenshots:
            if item.unquoted_inspect_link == unquoted_inspect_link:
                return item
        return None

    def screenshot(self, item: Item) -> None:
        payload = {
            "inspectLink": item.unquoted_inspect_link
        }
        try:
            response = requests.post("https://market-api.swap.gg/v1/screenshot", headers=self.headers, json=payload)
            data: SwapGGScreenshotResponse = response.json()
        except requests.RequestException:
            logger.warning("Failed to receive response")
            self.screenshots[item] = ScreenshotState.INVALID
            return

        if data["status"] != "OK":
            logging.warning("Failed to request screenshot")
            self.screenshots[item] = ScreenshotState.WAITING
            return
        if data["result"]["state"] == "COMPLETED":
            logger.debug("screenshot already taken!")
            image_link: str = data["result"]["imageLink"]
            item.image_link = image_link
            self.screenshots[item] = ScreenshotState.COMPLETE

    def close(self):
        self.socket.disconnect()

# def modify_inspect_link(inspect_link: str) -> str:
#     return inspect_link.replace("+", " ").replace("%20", " ")
#
#
# def take_screenshot(inspect_link: str) -> None:
#     inspect_link = modify_inspect_link(inspect_link)
#     screenshots[inspect_link] = None
#
#     payload = {
#         "inspectLink": inspect_link
#     }
#
#     logger.debug(f"Requesting screenshot for inspect link: {inspect_link}")
#     try:
#         response = requests.post("https://market-api.swap.gg/v1/screenshot", headers=this.headers, json=payload)
#         data: SwapGGScreenshotResponse = response.json()
#     except requests.RequestException:
#         logger.warning("Failed to receive response")
#         screenshots[inspect_link] = INVALID
#         return
#
#     if data["status"] != "OK":
#         logging.warning("Failed to request screenshot")
#         screenshots[inspect_link] = INVALID
#         return
#     if data["result"]["state"] == "COMPLETED":
#         logger.debug("screenshot already taken!")
#         image_link: str = data["result"]["imageLink"]
#         screenshots[inspect_link] = image_link


# def wait_for_screenshot(item: Item) -> None:
#     inspect_link = modify_inspect_link(inspect_link)
#     image_link: str | None | Type[INVALID] = screenshots.get(inspect_link)
#     if image_link is INVALID:
#         return
#     if image_link:
#         return image_link
#     while not image_link:
#         image_link = screenshots.get(inspect_link)
#         time.sleep(1)
#     return image_link


