from __future__ import annotations

import urllib.parse
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from csgoinspect.tweet import ItemsTweet


@dataclass
class Item:
    """Represents an Item in a CS:GO inventory."""
    _inspect_link: str
    _image_link: str | None = field(hash=False, default=None)
    _tweet: ItemsTweet = field(repr=False, hash=False, init=False, compare=False, default=None)

    @property
    def inspect_link(self) -> str:
        return self._inspect_link

    @inspect_link.setter
    def inspect_link(self, value: str) -> None:
        self._inspect_link = value

    @property
    def image_link(self) -> str:
        return self._image_link

    @image_link.setter
    def image_link(self, value: str) -> None:
        self._image_link = value
        self._tweet.alert_item_updated()

    @property
    def unquoted_inspect_link(self) -> str:
        return urllib.parse.unquote_plus(self.inspect_link)
