from __future__ import annotations

import logging
import os
from datetime import datetime
from typing import TYPE_CHECKING, Any

import redis

if TYPE_CHECKING:
    from csgoinspect.tweet import ItemsTweet

logger = logging.getLogger(__name__)


class Redis:
    """A wrapper class around redis for cache database interactions"""
    REDIS_HOST = os.environ["REDIS_HOST"]
    REDIS_PASSWORD = os.environ["REDIS_PASSWORD"]
    REDIS_PORT = int(os.environ["REDIS_PORT"])
    REDIS_DATABASE = int(os.environ["REDIS_DATABASE"])

    EX = 60 * 60 * 24 * 30  # month

    def __init__(self):
        self._redis = redis.Redis(
            host=self.REDIS_HOST,
            password=self.REDIS_PASSWORD,
            port=self.REDIS_PORT,
            db=self.REDIS_DATABASE
        )

    def already_responded(self, tweet: ItemsTweet) -> bool:
        tweet_value = self._redis.get(str(tweet.id))
        has_already_responded = tweet_value is not None
        if has_already_responded:
            logger.debug(f"already responded -- tweet: {tweet}")
        return has_already_responded

    def store_tweet(self, tweet: ItemsTweet) -> None:
        """Signifies that a Tweet has been responded to, and is therefore stored"""
        logger.debug(f"storing tweet data in redis for tweet: {tweet!r}")
        self._redis.set(name=str(tweet.id), value=datetime.now().isoformat(), ex=self.EX)


if __name__ == "__main__":
    redis = Redis()
