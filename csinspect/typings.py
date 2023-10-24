from __future__ import annotations

import typing as t
from typing import NamedTuple, TypedDict


class SwapGGSSuccessfulScreenshotResponse(TypedDict):
    status: str
    result: SwapGGScreenshotResult


class SwapGGErrorScreenshotResponse(TypedDict):
    time: int
    status: t.Literal["STEAM_ERROR"] | str


SwapGGScreenshotResponse: t.TypeAlias = SwapGGSSuccessfulScreenshotResponse | SwapGGErrorScreenshotResponse

class SwapGGScreenshotResult(TypedDict):
    imageId: str
    inspectLink: str
    marketName: str
    state: t.Literal["COMPLETED", "IN_QUEUE"] | str


class SwapGGScreenshotReady(TypedDict):
    imageId: str


class _BaseTweetResponseRawData(TypedDict):
    time: str
    successful: bool


class TweetResponseRawData(_BaseTweetResponseRawData, total=False):
    failed_attempts: int

class TweetResponseState(NamedTuple):
    successful: bool
    failed_attempts: int = 0
