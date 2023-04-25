from __future__ import annotations

import asyncio
import typing as t

import tweepy
import tweepy.errors
from loguru import logger

from csgoinspect import redis_, screenshot_tools, twitter
from csgoinspect.commons import (
    DEV_DONT_SEND_TWEETS,
    DEV_ID,
    INSPECT_LINK_QUERY,
    INSPECT_URL_REGEX,
    IS_DEV,
    LIVE_RULES,
    MAX_FAILED_ATTEMPTS,
    ONLY_RESPOND_TO_DEV,
    PREFER_SKINPORT,
    TWEET_EXPANSIONS,
    TWEET_TWEET_FIELDS,
    TWEET_USER_FIELDS,
)
from csgoinspect.item import Item
from csgoinspect.tweet import TweetWithItems

if t.TYPE_CHECKING:
    import re


class CSGOInspect:
    def __init__(self: CSGOInspect) -> None:
        self.screenshots = screenshot_tools.ScreenshotTools()
        self.twitter = twitter.Twitter()
        self.twitter.live.on_tweet = self.on_tweet

    async def on_tweet(self: CSGOInspect, tweet: tweepy.Tweet) -> None:
        tweet_with_items = await self._parse_tweet(tweet)
        if not tweet_with_items:
            return
        coro = self.process_tweet(tweet_with_items)
        asyncio.create_task(coro)

    async def find_tweets(self: CSGOInspect) -> list[TweetWithItems]:
        search_results: tweepy.Response = await self.twitter.v2.search_recent_tweets(
            query=INSPECT_LINK_QUERY,
            expansions=TWEET_EXPANSIONS,
            tweet_fields=TWEET_TWEET_FIELDS,
            user_fields=TWEET_USER_FIELDS,
        )  # type: ignore
        tweets: list[tweepy.Tweet] = search_results.data
        items_tweets: list[TweetWithItems] = []
        for tweet in tweets:
            tweet_with_items = await self._parse_tweet(tweet)
            if not tweet_with_items:
                continue
            items_tweets.append(tweet_with_items)
        return items_tweets

    async def run(self: CSGOInspect) -> None:
        async def incrementally_find_tweets() -> None:
            logger.debug("STARTING: INCREMENTALLY FIND TWEETS")
            while True:
                logger.info("FINDING TWEETS (Past 10 Minutes)")
                try:
                    items_tweets = await self.find_tweets()
                    await self.process_tweets(items_tweets)
                except Exception:
                    logger.exception("Error finding tweets")
                logger.info("DONE FINDING TWEETS (Past 10 Minutes)")
                await asyncio.sleep(600)

        task_one = asyncio.create_task(incrementally_find_tweets())

        await self.twitter.live.add_rules(LIVE_RULES)

        logger.debug("STARTING: LIVE TWEETS")

        task_two = self.twitter.live.filter(
            expansions=TWEET_EXPANSIONS, tweet_fields=TWEET_TWEET_FIELDS, user_fields=TWEET_USER_FIELDS
        )

        await asyncio.gather(task_one, task_two)

    async def process_tweet(self: CSGOInspect, tweet: TweetWithItems) -> None:
        logger.info(f"PROCESSING TWEET: {tweet.url}")

        prefer_skinport = PREFER_SKINPORT or await self._prefer_skinport(tweet)
        logger.debug(f"SCREENSHOT PREFER SKINPORT: {prefer_skinport}")

        screenshot_responses = await self.screenshots.screenshot_tweet(tweet, prefer_skinport=prefer_skinport)

        logger.debug(f"SCREENSHOT RESPONSES: {screenshot_responses}")

        if not any(screenshot_responses):
            logger.info(f"SKIPPING TWEET (Failed To Generate Screenshots): {tweet.url}")

            await redis_.update_tweet_state(tweet, successful=False)
            return

        logger.info(f"REPLYING TO TWEET: {tweet.url}")
        logger.debug(f"{tweet.items=}")

        if DEV_DONT_SEND_TWEETS:
            logger.info("SKIPPING TWEET (DEV_DONT_SEND_TWEETS IS ENABLED)")
            return

        try:
            await self.twitter.reply(tweet)
        except tweepy.errors.HTTPException as exc:
            logger.warning(f"ERROR REPLYING: {tweet.url} - {exc}")

            await redis_.update_tweet_state(tweet, successful=False)
            return

        logger.success(f"REPLIED TO TWEET: {tweet.url}")

        await redis_.update_tweet_state(tweet, successful=True)

    async def process_tweets(self: CSGOInspect, tweets: t.Iterable[TweetWithItems]) -> None:
        for tweet in tweets:
            coro = self.process_tweet(tweet)
            asyncio.create_task(coro)

    async def _prefer_skinport(self: CSGOInspect, tweet: TweetWithItems) -> bool:
        parent_tweet_id: int = tweet.tweet.conversation_id

        tweet_from_reference: tweepy.Response = await self.twitter.v2.get_tweet(parent_tweet_id, expansions="author_id")  # type: ignore
        tweet_users: list[tweepy.User] = tweet_from_reference.includes["users"]
        return any(user.username == "Skinport" for user in tweet_users)

    async def _parse_tweet(self: CSGOInspect, tweet: tweepy.Tweet) -> TweetWithItems | None:
        # Twitter only allows 4 images
        matches: list[re.Match] = list(INSPECT_URL_REGEX.finditer(tweet.text))
        matches = matches[:4]

        if not matches:
            logger.info(f"SKIPPING TWEET (No Inspect Links): {tweet.id} ")
            return None

        if DEV_ID:
            if IS_DEV and ONLY_RESPOND_TO_DEV and tweet.author_id != DEV_ID:
                logger.info(f"SKIPPING TWEET (Dev Mode & Not Dev): {tweet.id}, {tweet.author_id} ")
                return None
            if not IS_DEV and tweet.author_id == DEV_ID:
                logger.info(f"SKIPPING TWEET (Not Dev Mode & Dev): {tweet.id}, {tweet.author_id} ")
                return None

        items = tuple(Item(inspect_link=match.group()) for match in matches)

        tweet_with_items = TweetWithItems(items, tweet)
        tweet_state = await redis_.tweet_state(tweet_with_items)

        if tweet_state:
            if tweet_state.failed_attempts > MAX_FAILED_ATTEMPTS:
                logger.info(f"SKIPPING TWEET (Too Many Failed Attempts): {tweet.id}")
                return None

            if tweet_state.successful:
                logger.info(f"SKIPPING TWEET (Already Successfully Responded): {tweet.id}")
                return None

            tweet_with_items.failed_attempts = tweet_state.failed_attempts

        return tweet_with_items
