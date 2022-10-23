from __future__ import annotations

import urllib.parse
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from csgoinspect.typings import ItemScreenshotState

if TYPE_CHECKING:
    from csgoinspect.tweet import ItemsTweet


@dataclass
class Item:
    """Represents an Item in a CS:GO inventory."""
    inspect_link: str
    image_link: str | None = field(hash=False, default=None)
    state: ItemScreenshotState = field(hash=False, init=False, compare=False, default=ItemScreenshotState.INCOMPLETE)
    _tweet: ItemsTweet = field(repr=False, hash=False, init=False, compare=False, default=None)  # type: ignore

    def set_image_link(self, value: str) -> None:
        self.image_link = value
        self.trigger_finished()
        self._tweet.alert_item_updated()

    def trigger_start(self) -> None:
        self.state = ItemScreenshotState.INCOMPLETE

    def trigger_finished(self):
        self.state = ItemScreenshotState.FINISHED

    @property
    def unquoted_inspect_link(self) -> str:
        return urllib.parse.unquote_plus(self.inspect_link)
