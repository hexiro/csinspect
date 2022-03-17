from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING, Literal, Type

import requests
import socketio

if TYPE_CHECKING:
    from twitter_csgo_screenshot_bot.datatypes import SwapGGScreenshotResponse, ScreenshotReady


class INVALID:
    pass



socket = socketio.Client()
logger = logging.getLogger(__name__)
screenshots: dict[str, str | None | Type[INVALID]] = {}


def modify_inspect_link(inspect_link: str) -> str:
    return inspect_link.replace("+", " ").replace("%20", " ")


def take_screenshot(inspect_link: str) -> None:
    inspect_link = modify_inspect_link(inspect_link)
    screenshots[inspect_link] = None
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "en-US,en;q=0.9",
        "referer": "https://market.swap.gg/",
        "referrer-policy": "strict-origin-when-cross-origin",
    }
    payload = {
        "inspectLink": inspect_link
    }

    logger.debug(f"Requesting screenshot for inspect link: {inspect_link}")
    try:
        response = requests.post("https://market-api.swap.gg/v1/screenshot", headers=headers, json=payload)
        data: SwapGGScreenshotResponse = response.json()
    except requests.RequestException:
        logger.warning("Failed to receive response")
        screenshots[inspect_link] = INVALID

    try:
        if data["status"] != "OK":
            logging.warning("Failed to request screenshot")
            screenshots[inspect_link] = INVALID
            return
        if data["result"]["state"] == "COMPLETED":
            logger.debug("screenshot already taken!")
            image_link: str = data["result"]["imageLink"]
            screenshots[inspect_link] = image_link
            return
    except KeyError:
        logger.warning("Failed to parse response")
        logger.debug(f"{data=}")
        screenshots[inspect_link] = INVALID


def wait_for_screenshot(inspect_link: str) -> str | None:
    inspect_link = modify_inspect_link(inspect_link)
    image_link: str | None | Type[INVALID] = screenshots.get(inspect_link)
    if image_link is INVALID:
        return
    if image_link:
        return image_link
    while not image_link:
        image_link = screenshots.get(inspect_link)
        time.sleep(1)
    return image_link


@socket.on("connect")
def on_connect():
    logger.debug("connected to swap.gg socket.io websocket")


@socket.on("screenshot:ready")
def on_message(data: ScreenshotReady):
    logger.debug(f"SCREENSHOT:READY {data}")
    inspect_link = data["inspectLink"]
    image_link = data["imageLink"]
    if inspect_link in screenshots:
        logger.debug("screenshot data saved!")
        screenshots[inspect_link] = image_link


socket.connect('wss://market-ws.swap.gg')
