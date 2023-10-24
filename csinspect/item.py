from __future__ import annotations

import urllib.parse
from dataclasses import dataclass, field


@dataclass(unsafe_hash=True, slots=True)
class Item:
    """Represents an Item in a Counter-Strike inventory."""

    inspect_link: str = field(hash=True)
    image_id: str | None = field(compare=False, init=False, hash=False, default=None)

    @property
    def image_link(self) -> str:
        return f"https://s.swap.gg/{self.image_id}.jpg"

    @property
    def unquoted_inspect_link(self: Item) -> str:
        return urllib.parse.unquote_plus(self.inspect_link)
