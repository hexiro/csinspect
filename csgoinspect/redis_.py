"""A wrapper around redis for cache database interactions"""

from __future__ import annotations

from datetime import datetime
from functools import lru_cache
from typing import TYPE_CHECKING

from redis.asyncio import Redis
from loguru import logger

from csgoinspect.commons import REDIS_HOST, REDIS_PASSWORD, REDIS_PORT, REDIS_DATABASE, REDIS_EX

if TYPE_CHECKING:
    from csgoinspect.tweet import TweetWithItems


@lru_cache(maxsize=None)
def get_redis() -> Redis:
    return Redis(host=REDIS_HOST, password=REDIS_PASSWORD, port=REDIS_PORT, db=REDIS_DATABASE)


async def has_responded(tweet: TweetWithItems) -> bool:
    redis_ = get_redis()
    tweet_value = await redis_.get(str(tweet.id))
    has_already_responded = tweet_value is not None
    if has_already_responded:
        logger.debug(f"already responded -- tweet: {tweet}")
    return has_already_responded


async def mark_responded(tweet: TweetWithItems) -> None:
    """Signifies that a Tweet has been responded to, and is therefore stored"""
    redis_ = get_redis()
    logger.debug(f"storing tweet data in redis for tweet: {tweet!r}")
    await redis_.set(name=str(tweet.id), value=datetime.now().isoformat(), ex=REDIS_EX)
