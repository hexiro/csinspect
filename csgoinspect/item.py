from __future__ import annotations

import urllib.parse
from typing import Optional, Callable, TYPE_CHECKING

import attrs

from csgoinspect import commons
from csgoinspect.exceptions import InvalidInspectLink

if TYPE_CHECKING:
    from csgoinspect.typings import Tweet


def _inspect_link_validator(value: str) -> None:
    if commons.INSPECT_URL_REGEX.match(value) is None:
        raise InvalidInspectLink("inspect_link passed is not valid.")


def inspect_link_validator(self: Item, attribute: attrs.Attribute, value: str) -> None:
    _inspect_link_validator(value)


@attrs.define(slots=True, hash=True, frozen=False)
class Item:
    """Represents an Item in a CS:GO inventory."""
    _inspect_link: str = attrs.field(validator=inspect_link_validator)
    _image_link: Optional[str] = None
    _callback: Callable[[Item, Tweet], None] = attrs.field(repr=False, hash=False, init=False, default=None)
    _tweet: Tweet = attrs.field(repr=False, hash=False, init=False, default=None)

    @property
    def inspect_link(self) -> str:
        return self._inspect_link

    @property
    def image_link(self) -> str:
        return self._image_link

    @inspect_link.setter
    def inspect_link(self, value: str) -> None:
        _inspect_link_validator(value)
        self._inspect_link = value

    @image_link.setter
    def image_link(self, value: str) -> None:
        self._image_link = value
        self.execute_callback()

    @property
    def unquoted_inspect_link(self) -> str:
        return urllib.parse.unquote_plus(self.inspect_link)

    def register_callback(self, func: Callable, tweet: Tweet) -> None:
        self._callback = func
        self._tweet = tweet

    def execute_callback(self) -> None:
        self._callback(self, self._tweet)
