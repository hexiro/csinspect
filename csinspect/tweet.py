from __future__ import annotations

import typing as t
from dataclasses import dataclass

if t.TYPE_CHECKING:
    import tweepy

    from csinspect.item import Item


@dataclass(slots=True)
class TweetWithInspectLink:
    """A Tweet that also contains inspect-links pointing to Counter-Strike items."""

    items: tuple[Item, ...]
    tweet: tweepy.Tweet

    @property
    def id(self: TweetWithInspectLink) -> int:
        return self.tweet.id  # type: ignore[no-any-return]

    @property
    def author_id(self: TweetWithInspectLink) -> int:
        return self.tweet.author_id  # type: ignore[no-any-return]

    @property
    def url(self: TweetWithInspectLink) -> str:
        return f"https://twitter.com/i/web/status/{self.id}"
