from __future__ import annotations

import urllib.parse
from dataclasses import dataclass, field


@dataclass
class Item:
    """Represents an Item in a CS:GO inventory."""

    inspect_link: str
    image_link: str | None = field(compare=False, init=False, default=None)
    # False if not waiting on screenshot
    is_ready: bool = field(compare=False, init=False, default=False)

    @property
    def unquoted_inspect_link(self) -> str:
        return urllib.parse.unquote_plus(self.inspect_link)
