from __future__ import annotations

from loguru import logger

from csgoinspect.swapgg import SwapGG
from csgoinspect.twitter import Twitter


def main() -> None:
    twitter = Twitter()
    swap_gg = SwapGG()
    try:
        # TODO: improve redis handling
        # TODO: FIND TWEETS VIA INVENTORY LINK
        # TODO: async?
        for tweet in twitter.find_tweets():
            logger.info(f"handling tweet: {tweet!r}")
            for item in tweet.items:
                swap_gg.screenshot(item)

        for tweet in twitter.live():
            logger.info(f"handling tweet: {tweet!r}")
            for item in tweet.items:
                swap_gg.screenshot(item)
    finally:
        swap_gg.close()


if __name__ == "__main__":
    main()
