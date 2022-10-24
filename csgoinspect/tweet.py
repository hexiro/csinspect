from __future__ import annotations

import typing as t
from dataclasses import dataclass

if t.TYPE_CHECKING:
    import tweepy

    from csgoinspect.item import Item


@dataclass
class TweetWithItems:
    """A Tweet that also contains data about CS:GO items."""

    items: tuple[Item, ...]
    tweet: tweepy.Tweet

    @property
    def id(self) -> int:
        return self.tweet.id  # type: ignore[no-any-return]

    @property
    def url(self) -> str:
        return f"https://twitter.com/i/web/status/{self.id}"

    @property
    def is_ready(self) -> bool:
        return all(item.is_ready for item in self.items)
