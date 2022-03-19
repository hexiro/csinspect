from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import attrs

if TYPE_CHECKING:
    from csgoinspect.item import Item
    from csgoinspect.twitter import Twitter

logger = logging.getLogger(__name__)


@attrs.define(slots=True, hash=True, frozen=False)
class Tweet:
    """Represents an Item in a CS:GO inventory."""
    id: int
    text: str
    user_screen_name: str
    has_photo: bool
    items: list[Item] = attrs.field(hash=False)
    _twitter: Twitter = attrs.field(repr=False, hash=False)

    @property
    def id_str(self) -> str:
        return str(self.id)

    @property
    def url(self) -> str:
        return f"https://twitter.com/i/web/status/{self.id_str}"

    def assign_items(self, *items: Item):
        self.items.extend(items)

    def alert_item_updated(self) -> None:
        if not all(i.image_link for i in self.items):
            return
        self.reply()

    def reply(self) -> None:
        media_uploads = self._twitter.upload_items(self.items)
        self._twitter._twitter.update_status(
            status=f"@{self.user_screen_name}",
            in_reply_to_status_id=self.id_str,
            media_ids=[media_upload.media_id for media_upload in media_uploads]
        )
