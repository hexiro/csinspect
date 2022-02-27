from __future__ import annotations

from typing import TypedDict, Literal


class SwapGGScreenshotResponse(TypedDict):
    time: int
    status: str
    result: CompletedResult | NotCompletedResult


class NotCompletedResult(TypedDict):
    marketName: str
    inspectLink: str
    state: str
    itemInfo: object  # typings not needed


class CompletedResult(TypedDict):
    marketName: str
    inspectLink: str
    state: Literal["COMPLETED"]
    itemInfo: object  # typings not needed
    imageLink: str


class ScreenshotReady(TypedDict):
    imageLink: str
    inspectLink: str
