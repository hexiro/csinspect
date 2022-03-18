from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from csgoinspect.swapgg import SwapGG
from csgoinspect.twitter import Twitter

if TYPE_CHECKING:
    from csgoinspect.typings import Tweet

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

def tweet_callback(tweet: Tweet) -> None:
    print(f"callback {tweet=}")


def main() -> None:
    twitter = Twitter()
    swap_gg = SwapGG()

    # TODO: use twitter stream
    # https://docs.tweepy.org/en/v4.7.0/streaming.html#streaming
    # https://docs.tweepy.org/en/v4.7.0/extended_tweets.html

    # TODO: construct Tweet dataclass as a wrapper around tweepy.models.Status
    # TODO: and validate there instead of validating everytime a tweet is referenced

    for tweet in twitter.fetch_tweets():
        tweet.register_callback(tweet_callback)
        for item in tweet.items:
            swap_gg.screenshot(item)


if __name__ == "__main__":
    main()
