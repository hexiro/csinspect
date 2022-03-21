from __future__ import annotations

from loguru import logger

from csgoinspect.redis_ import Redis
from csgoinspect.swapgg import SwapGG
from csgoinspect.twitter import Twitter


def main() -> None:
    twitter = Twitter()
    swap_gg = SwapGG()
    redis = Redis()
    try:
        # TODO: improve redis handling
        # TODO: FIND TWEETS VIA INVENTORY LINK
        # TODO: move away from attrs
        # TODO: async?
        for tweet in twitter.find_tweets():
            if redis.already_responded(tweet):
                continue
            logger.info(f"handling tweet: {tweet!r}")
            for item in tweet.items:
                swap_gg.screenshot(item)
            redis.store_tweet(tweet)

        for tweet in twitter.live():
            logger.info(f"handling tweet: {tweet!r}")
            for item in tweet.items:
                swap_gg.screenshot(item)
            redis.store_tweet(tweet)
    finally:
        swap_gg.close()


if __name__ == "__main__":
    main()
