from __future__ import annotations

import time
from typing import TYPE_CHECKING

import requests
import socketio

if TYPE_CHECKING:
    from twitter_csgo_screenshot_bot.datatypes import SwapGGScreenshotResponse, ScreenshotReady

sio = socketio.Client()

screenshots: dict[str, str | None] = {}


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
    response = requests.post("https://market-api.swap.gg/v1/screenshot", headers=headers, json=payload)
    data: SwapGGScreenshotResponse = response.json()

    if data["status"] != "OK":
        raise Exception("oops?")
    if data["result"]["state"] == "COMPLETED":
        image_link: str = data["result"]["imageLink"]
        screenshots[inspect_link] = image_link


def wait_for_screenshot(inspect_link: str) -> str | None:
    inspect_link = modify_inspect_link(inspect_link)
    image_link: str | None = screenshots.get(inspect_link)
    if image_link:
        return image_link
    while not image_link:
        image_link = screenshots.get(inspect_link)
        time.sleep(1)


@sio.on("connect")
def on_connect():
    print("I'm connected!")


@sio.on("screenshot:ready")
def on_message(data: ScreenshotReady):
    print(data)
    inspect_link = data["inspectLink"]
    image_link = data["imageLink"]
    if inspect_link in screenshots:
        screenshots[inspect_link] = image_link


sio.connect('wss://market-ws.swap.gg')
