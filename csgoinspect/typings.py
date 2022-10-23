from __future__ import annotations

import typing as t
from typing import TypedDict


class SwapGGScreenshotResponse(TypedDict):
    time: int
    status: str
    result: ScreenshotCompletedResult | ScreenshotNotCompletedResult


class ScreenshotNotCompletedResult(TypedDict):
    marketName: str
    inspectLink: str
    state: str
    itemInfo: object  # typings not needed


class ScreenshotCompletedResult(TypedDict):
    marketName: str
    inspectLink: str
    imageLink: str
    state: t.Literal["COMPLETED"]
    itemInfo: object  # typings not needed


class ScreenshotReady(TypedDict):
    imageLink: str
    inspectLink: str
