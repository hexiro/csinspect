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
    from csgoinspect.typings import TweetResponseRawData


@lru_cache(maxsize=None)
def get_redis() -> Redis:
    return Redis(host=REDIS_HOST, password=REDIS_PASSWORD, port=REDIS_PORT, db=REDIS_DATABASE)


async def tweet_state(tweet: TweetWithItems) -> TweetResponseState | None:
    redis_ = get_redis()

    key = str(tweet.id)
    tweet_value: bytes | None = await redis_.get(key)

    if not tweet_value:
        return None

    data: TweetResponseRawData = json.loads(tweet_value)

    return TweetResponseState(data["successful"])


async def update_tweet_state(tweet: TweetWithItems, *, successful: bool) -> None:
    redis_ = get_redis()

    logger.debug(f"STORING TWEET: {tweet.url}")

    data: TweetResponseRawData = {"successful": successful, "time": datetime.now().isoformat()}

    if not successful:
        state = await tweet_state(tweet)
        if state:
            data["failed_attempts"] = state.failed_attempts + 1

    await redis_.set(name=str(tweet.id), value=json.dumps(data), ex=REDIS_EX)
