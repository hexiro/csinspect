"""A wrapper around redis for cache database interactions"""

from __future__ import annotations

from datetime import datetime
from functools import cache
from typing import TYPE_CHECKING

import redis
from loguru import logger

from csgoinspect.commons import REDIS_HOST, REDIS_EX

if TYPE_CHECKING:
    from csgoinspect.tweet import ItemsTweet


@cache
def get_redis() -> redis.Redis:
    return redis.Redis(host=REDIS_HOST)


def already_responded(tweet: ItemsTweet) -> bool:
    redis_ = get_redis()
    tweet_value = redis_.get(str(tweet.id))
    has_already_responded = tweet_value is not None
    if has_already_responded:
        logger.debug(f"already responded -- tweet: {tweet}")
    return has_already_responded


def store_tweet(tweet: ItemsTweet) -> None:
    """Signifies that a Tweet has been responded to, and is therefore stored"""
    redis_ = get_redis()
    logger.debug(f"storing tweet data in redis for tweet: {tweet!r}")
    redis_.set(name=str(tweet.id), value=datetime.now().isoformat(), ex=REDIS_EX)
