from __future__ import annotations

import asyncio
import io
import typing as t

import httpx
import tweepy
import tweepy.asynchronous
import tweepy.errors
from loguru import logger

from csgoinspect.config import (
    ENABLE_TWITTER_LIVE,
    TWITTER_ACCESS_TOKEN,
    TWITTER_ACCESS_TOKEN_SECRET,
    TWITTER_API_KEY,
    TWITTER_API_KEY_SECRET,
    TWITTER_BEARER_TOKEN,
)

if t.TYPE_CHECKING:
    from tweepy.models import Media

    from csgoinspect.item import Item
    from csgoinspect.tweet import TweetWithItems


class Twitter:
    """Merged wrapper of Twitter's v1, v2, and Steaming API provided by Tweepy."""

    def __init__(self: Twitter, on_tweet: t.Callable[[tweepy.Tweet], t.Coroutine[t.Any, t.Any, None]]) -> None:
        self.v2 = tweepy.asynchronous.AsyncClient(
            bearer_token=TWITTER_BEARER_TOKEN,
            consumer_key=TWITTER_API_KEY,
            consumer_secret=TWITTER_API_KEY_SECRET,
            access_token=TWITTER_ACCESS_TOKEN,
            access_token_secret=TWITTER_ACCESS_TOKEN_SECRET,
        )
        self.v1 = tweepy.API(
            tweepy.OAuthHandler(
                consumer_key=TWITTER_API_KEY,
                consumer_secret=TWITTER_API_KEY_SECRET,
                access_token=TWITTER_ACCESS_TOKEN,
                access_token_secret=TWITTER_ACCESS_TOKEN_SECRET,
            )
        )

        self.live: tweepy.asynchronous.AsyncStreamingClient | None = None
        if ENABLE_TWITTER_LIVE:
            self.live = tweepy.asynchronous.AsyncStreamingClient(TWITTER_BEARER_TOKEN)

            async def on_connect() -> None:
                logger.debug("CONNECTED: Twitter Streaming API")

            async def on_disconnect() -> None:
                logger.debug("CONNECTED: Twitter Streaming API")

            self.live.on_connect = on_connect
            self.live.on_disconnect = on_disconnect

    async def reply(self: Twitter, tweet: TweetWithItems) -> None:
        media_uploads = await self.upload_items(tweet.items)
        media_ids: list[int] = [media.media_id for media in media_uploads]  # type: ignore

        await self.v2.create_tweet(in_reply_to_tweet_id=tweet.id, media_ids=media_ids)

    async def upload_items(self: Twitter, items: t.Iterable[Item]) -> list[Media]:
        async def fetch_screenshot(session: httpx.AsyncClient, image_link: str) -> tuple[str, io.BytesIO]:
            screenshot = await session.get(image_link)
            return (image_link, io.BytesIO(screenshot.content))

        async with httpx.AsyncClient() as session:
            screenshot_tasks: list[asyncio.Task[tuple[str, io.BytesIO]]] = []

            for item in items:
                if not item.image_link:
                    continue

                screenshot_coro = fetch_screenshot(session, item.image_link)
                screenshot_task = asyncio.create_task(screenshot_coro)  # type: ignore

                screenshot_tasks.append(screenshot_task)

            screenshots: list[tuple[str, io.BytesIO]] = await asyncio.gather(*screenshot_tasks)

        media_tasks: list[asyncio.Task[Media]] = []
        for image_link, screenshot in screenshots:
            media_coro = self.media_upload(filename=image_link, file=screenshot)
            media_task = asyncio.create_task(media_coro)
            media_tasks.append(media_task)

        media_uploads: list[Media] = await asyncio.gather(*media_tasks)
        return media_uploads

    async def media_upload(
        self: Twitter,
        filename: str | None,
        *,
        file: io.BytesIO | None = None,
        chunked: bool = False,
        # https://developer.twitter.com/en/docs/twitter-api/v1/media/upload-media/api-reference/post-media-upload
        media_category: t.Literal["amplify_video", "tweet_gif", "tweet_image", "tweet_video"] | None = None,
        additional_owners: str | None = None,
        **kwargs: t.Any,
    ) -> Media:
        # Uses Twitter v1 API (no async support with tweepy) so we need to run in executor
        return await asyncio.to_thread(
            self.v1.media_upload,  # type: ignore
            filename=filename,
            file=file,
            chunked=chunked,
            media_category=media_category,
            additional_owners=additional_owners,
            **kwargs,
        )  # type: ignore
