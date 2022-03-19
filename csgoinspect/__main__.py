from __future__ import annotations

import logging
from datetime import datetime

from csgoinspect.redis_ import Redis
from csgoinspect.swapgg import SwapGG
from csgoinspect.twitter import Twitter

logger = logging.getLogger(__name__)


def main() -> None:
    twitter = Twitter()
    swap_gg = SwapGG()
    redis = Redis()

    # TODO: ALSO CHECK TWEETS OF PAST WEEK THEN DO LIVE
    # TODO: ALSO SEARCH FOR INVENTORY URLS
    # TODO: logging

    for tweet in twitter.live():
        print(f"tweet! {tweet=}")
        # potentially already has screenshot (this conditional could be subject to change)
        if tweet.attachments:
            print("skipping! has attachments")
            continue
        # if redis.already_responded(tweet):
        #     print("already responded to:")
        #     continue
        for item in tweet.items:
            swap_gg.screenshot(item)
        redis.store_tweet(tweet, value=datetime.now().isoformat())

if __name__ == "__main__":
    main()
