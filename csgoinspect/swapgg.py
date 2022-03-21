from __future__ import annotations

from typing import TYPE_CHECKING

import requests
import socketio
from loguru import logger

if TYPE_CHECKING:
    from csgoinspect.typings import SwapGGScreenshotResponse, ScreenshotReady
    from csgoinspect.item import Item

headers = {
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://market.swap.gg/",
    "Referrer-Policy": "strict-origin-when-cross-origin",
}
screenshot_queue: list[Item] = []
socket = socketio.Client(handle_sigint=True)


@socket.on("connect")
def on_connect():
    logger.debug("connected to swap.gg websocket")


@socket.on("disconnect")
def on_disconnect():
    logger.warning("disconnected from swap.gg websocket")


def find_item(unquoted_inspect_link: str) -> Item | None:
    for item in screenshot_queue:
        if item.unquoted_inspect_link == unquoted_inspect_link:
            return item
    return None


@socket.on("screenshot:ready")
def on_screenshot(data: ScreenshotReady):
    unquoted_inspect_link = data["inspectLink"]
    image_link = data["imageLink"]

    if item := find_item(unquoted_inspect_link):
        logger.debug(f"saved image link for item: {item}")
        item.set_image_link(image_link)
        screenshot_queue.remove(item)
    else:
        logger.debug(f"received image_link for item with inspect_link: {unquoted_inspect_link}")


def screenshot(item: Item) -> None:
    payload = {
        "inspectLink": item.unquoted_inspect_link
    }

    logger.debug(f"requesting screenshot for item: {item}")
    logger.debug(f"payload: {payload}")

    try:
        response = requests.post("https://market-api.swap.gg/v1/screenshot", headers=headers, json=payload)
        data: SwapGGScreenshotResponse = response.json()
    except requests.RequestException:
        logger.warning(f"Failed to receive response for item: {item}")
        return

    if data["status"] != "OK":
        logger.warning(f"Failed to request screenshot for item: {item}")
        item.trigger_finished()
    elif data["result"]["state"] == "COMPLETED":
        logger.debug(f"screenshot already taken for item: {item}")
        item.set_image_link(data["result"]["imageLink"])
    else:
        logger.debug(f"screenshotting -- inspect link: {item.unquoted_inspect_link}")
        screenshot_queue.append(item)


def disconnect():
    socket.disconnect()


socket.connect("wss://market-ws.swap.gg")
