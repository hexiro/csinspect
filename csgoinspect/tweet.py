from __future__ import annotations

import typing as t
from dataclasses import dataclass

if t.TYPE_CHECKING:
    import tweepy

    from csgoinspect.item import Item


@dataclass(slots=True)
class TweetWithItems:
    """A Tweet that also contains data about CS:GO items."""

    items: tuple[Item, ...]
    tweet: tweepy.Tweet
    failed_attempts: int = 0

    @property
    def id(self: TweetWithItems) -> int:
        return self.tweet.id  # type: ignore[no-any-return]

    @property
    def author_id(self: TweetWithItems) -> int:
        return self.tweet.author_id  # type: ignore[no-any-return]

    @property
    def url(self: TweetWithItems) -> str:
        return f"https://twitter.com/i/web/status/{self.id}"
