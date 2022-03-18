from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import TypedDict, Literal


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
    state: Literal["COMPLETED"]
    itemInfo: object  # typings not needed
    imageLink: str


class ScreenshotReady(TypedDict):
    imageLink: str
    inspectLink: str
