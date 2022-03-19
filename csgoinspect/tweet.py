from __future__ import annotations

import io
import logging
from typing import TYPE_CHECKING

import requests
import tweepy.models

if TYPE_CHECKING:
    from csgoinspect.twitter import Twitter
    from csgoinspect.item import Item

logger = logging.getLogger(__name__)


class ItemsTweet(tweepy.Tweet):
    """A Tweet that also contains data about CS:GO items."""

    def __init__(self, data):
        super().__init__(data)
        self.items: list[Item] = []
        self._twitter: Twitter = None

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id!r} text={self.text!r} items={self.items!r}>"

    def assign_items(self, *items: Item):
        self.items.extend(items)

    def alert_item_updated(self) -> None:
        if not all(i.image_link for i in self.items):
            return
        self.reply()

    def _upload_items(self) -> list[tweepy.models.Media]:
        media_uploads: list[tweepy.models.Media] = []
        for item in self.items:
            screenshot = requests.get(item.image_link)
            screenshot_file = io.BytesIO(screenshot.content)
            media: tweepy.models.Media = self._twitter.media_upload(filename=item.image_link, file=screenshot_file)
            media_uploads.append(media)
        return media_uploads

    def reply(self):
        media_uploads = self._upload_items()
        media_ids = [media.media_id for media in media_uploads]
        self._twitter.create_tweet(in_reply_to_tweet_id=self.id, media_ids=media_ids)