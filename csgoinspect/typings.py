from __future__ import annotations

from typing import TYPE_CHECKING

import tweepy.models

if TYPE_CHECKING:
    from typing import TypedDict, Literal, TypeAlias

Tweet: TypeAlias = tweepy.models.Status


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
