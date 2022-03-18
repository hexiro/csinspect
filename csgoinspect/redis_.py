from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any

import redis

if TYPE_CHECKING:
    from csgoinspect.tweet import Tweet

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

    def already_responded(self, tweet: Tweet) -> bool:
        tweet_value = self._redis.get(tweet.id_str)
        return tweet_value is not None

    def store_tweet(self, tweet: Tweet, value: Any) -> None:
        """Signifies that a Tweet has been responded to, and is therefore stored"""
        self._redis.set(name=tweet.id_str, value=value, ex=self.EX)


if __name__ == "__main__":
    redis = Redis()
