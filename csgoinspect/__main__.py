from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING

from redis import Redis

from csgoinspect.swapgg import SwapGG
from csgoinspect.twitter import Twitter

if TYPE_CHECKING:
    from csgoinspect.typings import Tweet
    from csgoinspect.item import Item



redis = Redis(
    host=os.environ["REDIS_HOST"],
    password=os.environ["REDIS_PASSWORD"],
    port=int(os.environ["REDIS_PORT"]),
    db=int(os.environ["REDIS_DATABASE"])
)

logger = logging.getLogger(__name__)


# def already_has_screenshot(tweet: tweepy.models.Status) -> bool:
#     try:
#         if tweet.extended_entities["media"]:
#             return True
#     except (AttributeError, KeyError):
#         pass
#     return False
#
#
# def already_responded(tweet: tweepy.models.Status) -> bool:
#     try:
#         status_id = tweet.id_str
#     except AttributeError:
#         return True
#     return redis.get(status_id) is not None
#
#
# def tweet_to_url(tweet: tweepy.models.Status) -> str:
#     return f"https://twitter.com/i/web/status/{tweet.id_str}"


def main() -> None:
    twitter = Twitter()
    swap_gg = SwapGG()

    def callback(item: Item, tweet: Tweet) -> None:
        print("callback")
        print(f"{item=} {tweet=}")
        swap_gg.close()

    for tweet, items in twitter.fetch_tweets().items():
        for item in items:
            item.register_callback(callback, tweet)
            swap_gg.screenshot(item)


if __name__ == "__main__":
    main()
