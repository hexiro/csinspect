from __future__ import annotations

from enum import Enum, auto
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import TypedDict, Literal


class ItemScreenshotState(Enum):
    INCOMPLETE = auto()  # hasn't started or waiting
    FINISHED = auto()    # finished or failed to fetch


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
