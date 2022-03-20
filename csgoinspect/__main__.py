from __future__ import annotations

import logging

from csgoinspect.redis_ import Redis
from csgoinspect.swapgg import SwapGG
from csgoinspect.twitter import Twitter

logger = logging.getLogger(__name__)


def main() -> None:
    twitter = Twitter()
    swap_gg = SwapGG()
    redis = Redis()
    try:
        # TODO: improve redis handling
        # TODO: FIND TWEETS VIA INVENTORY LINK
        # TODO: async?

        for tweet in twitter.find_tweets():
            if redis.already_responded(tweet):
                continue
            for item in tweet.items:
                swap_gg.screenshot(item)
            redis.store_tweet(tweet)

        for tweet in twitter.live():
            for item in tweet.items:
                swap_gg.screenshot(item)
            redis.store_tweet(tweet)
    finally:
        swap_gg.close()


if __name__ == "__main__":
    main()
