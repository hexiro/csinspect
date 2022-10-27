"""A wrapper around redis for cache database interactions"""

from __future__ import annotations

import json
import typing as t
from datetime import datetime
from functools import lru_cache

from loguru import logger
from redis.asyncio import Redis

from csgoinspect.commons import REDIS_DATABASE, REDIS_EX, REDIS_HOST, REDIS_PASSWORD, REDIS_PORT
from csgoinspect.typings import TweetResponseState

if t.TYPE_CHECKING:
    from csgoinspect.tweet import TweetWithItems
    from csgoinspect.typings import TweetResponseDataDict


@lru_cache(maxsize=None)
def get_redis() -> Redis:
    return Redis(host=REDIS_HOST, password=REDIS_PASSWORD, port=REDIS_PORT, db=REDIS_DATABASE)


async def response_state(tweet: TweetWithItems) -> TweetResponseState:
    redis_ = get_redis()

    key = str(tweet.id)
    tweet_value: bytes | None = await redis_.get(key)

    if not tweet_value:
        return TweetResponseState.NOT_RESPONDED

    data: TweetResponseDataDict

    try:
        data = json.loads(tweet_value)
    except json.JSONDecodeError:
        data = {"state": TweetResponseState.SUCCESSFUL.value, "time": tweet_value.decode()}
        await redis_.set(name=key, value=json.dumps(data), ex=REDIS_EX)

    return TweetResponseState(data["state"])


async def mark_responded(tweet: TweetWithItems, new_state: TweetResponseState) -> None:
    """Signifies that a Tweet has been responded to, and is therefore stored"""
    redis_ = get_redis()

    logger.debug(f"STORING TWEET: {tweet.url}")

    data: TweetResponseDataDict = {"state": new_state.value, "time": datetime.now().isoformat()}

    await redis_.set(name=str(tweet.id), value=json.dumps(data), ex=REDIS_EX)
