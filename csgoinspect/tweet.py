from __future__ import annotations

from typing import TYPE_CHECKING

import attrs

if TYPE_CHECKING:
    from csgoinspect.item import Item
    from typing import Callable, TypeAlias

    Callback: TypeAlias = Callable[["Tweet"], None]


@attrs.define(slots=True, hash=True, frozen=False)
class Tweet:
    """Represents an Item in a CS:GO inventory."""
    id: int
    text: str
    items: list[Item] = attrs.field(hash=False, default=attrs.Factory(list))
    _callback: Callback = attrs.field(repr=False, hash=False, init=False, default=None)

    @property
    def id_str(self) -> str:
        return str(self.id)

    def assign_items(self, *items: Item):
        self.items.extend(items)

    def register_callback(self, callback: Callback) -> None:
        self._callback = callback

    def alert_item_updated(self) -> None:
        if not all(i.image_link for i in self.items):
            return
        self._callback(self)
