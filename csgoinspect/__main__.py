from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from csgoinspect.redis_ import Redis
from csgoinspect.swapgg import SwapGG
from csgoinspect.twitter import Twitter

if TYPE_CHECKING:
    from csgoinspect.tweet import Tweet

logger = logging.getLogger(__name__)


def tweet_callback(tweet: Tweet) -> None:
    print(f"callback {tweet.url} {tweet=}")


def main() -> None:
    twitter = Twitter()
    swap_gg = SwapGG()
    redis = Redis()

    # TODO: use twitter stream
    # https://docs.tweepy.org/en/v4.7.0/streaming.html#streaming
    # https://docs.tweepy.org/en/v4.7.0/extended_tweets.html

    for tweet in twitter.fetch_tweets():
        # potentially already has screenshot (this conditional could be subject to change)
        if tweet.has_photo:
            print("has photo:", tweet)
            continue
        if redis.already_responded(tweet):
            print("already responded to:", tweet)
            continue
        tweet.register_callback(tweet_callback)
        for item in tweet.items:
            swap_gg.screenshot(item)


if __name__ == "__main__":
    main()
