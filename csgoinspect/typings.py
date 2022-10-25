from __future__ import annotations

import typing as t
from typing import TypedDict


class SwapGGSSuccessfulScreenshotResponse(TypedDict):
    time: int
    status: str
    result: SwapGGScreenshotCompletedResult | SwapGGScreenshotNotCompletedResult


class SwapGGErrorScreenshotResponse(TypedDict):
    time: int
    status: t.Literal["STEAM_ERROR"] | str


SwapGGScreenshotResponse: t.TypeAlias = SwapGGSSuccessfulScreenshotResponse | SwapGGErrorScreenshotResponse


class SwapGGScreenshotNotCompletedResult(TypedDict):
    marketName: str
    inspectLink: str
    state: str
    itemInfo: object  # typings not needed


class SwapGGScreenshotCompletedResult(TypedDict):
    marketName: str
    inspectLink: str
    imageLink: str
    state: t.Literal["COMPLETED"]
    itemInfo: object  # typings not needed


SwapGGScreenshotResult: t.TypeAlias = SwapGGScreenshotCompletedResult | SwapGGScreenshotNotCompletedResult


class SwapGGScreenshotReady(TypedDict):
    imageLink: str
    inspectLink: str
