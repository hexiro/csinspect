from __future__ import annotations

import logging
import time
from typing import re

import tweepy.models

from csgoinspect.commons import TWITTER_BEARER_TOKEN, TWITTER_API_KEY, TWITTER_API_KEY_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET, \
    INSPECT_URL_REGEX, LIVE_RULES, INSPECT_LINK_QUERY
from csgoinspect.item import Item
from csgoinspect.tweet import ItemsTweet

logger = logging.getLogger(__name__)

class Twitter(tweepy.Client):
    """Merged wrapper of v1, v2, and Streaming APIs provided by Tweepy."""

    TWEET_EXPANSIONS = ["referenced_tweets.id", "author_id", "referenced_tweets.id.author_id", "attachments.media_keys"]
    TWEET_TWEET_FIELDS = ["id", "text", "attachments"]
    TWEET_USER_FIELDS = ["id", "name", "username"]

    def __init__(self):
        super().__init__(
            bearer_token=TWITTER_BEARER_TOKEN,
            consumer_key=TWITTER_API_KEY,
            consumer_secret=TWITTER_API_KEY_SECRET,
            access_token=TWITTER_ACCESS_TOKEN,
            access_token_secret=TWITTER_ACCESS_TOKEN_SECRET
        )
        self._items_tweets: list[ItemsTweet] = []

        self._twitter_v1 = tweepy.API(tweepy.OAuthHandler(
            consumer_key=TWITTER_API_KEY,
            consumer_secret=TWITTER_API_KEY_SECRET,
            access_token=TWITTER_ACCESS_TOKEN,
            access_token_secret=TWITTER_ACCESS_TOKEN_SECRET
        ))

        self._live_twitter = tweepy.StreamingClient(TWITTER_BEARER_TOKEN)
        self._live_twitter.add_rules(LIVE_RULES)
        self._live_twitter.on_connect = self.on_connect
        self._live_twitter.on_disconnect = self.on_disconnect
        self._live_twitter.on_tweet = self.on_tweet

    @staticmethod
    def on_connect():
        logger.debug("connected!")

    @staticmethod
    def on_disconnect():
        logger.error("disconnected from Twitter :(")

    def on_tweet(self, tweet: tweepy.Tweet):
        items_tweet = self._tweet_to_items_tweet(tweet)
        if not items_tweet:
            return
        self._items_tweets.append(items_tweet)

    def live(self):
        if not self._live_twitter.running:
            self._start()
        while True:
            if self._items_tweets:
                items_tweet = self._items_tweets.pop(0)
                logger.info(f"received new tweet: {items_tweet!r}")
                yield items_tweet
            time.sleep(10)

    def _tweet_to_items_tweet(self, tweet: tweepy.Tweet) -> ItemsTweet | None:
        # Twitter only allows 4 images
        matches: list[re.Match] = list(INSPECT_URL_REGEX.finditer(tweet.text))
        matches = matches[:4]
        if not matches:
            logger.debug(f"tweet: {tweet} -- has no inspect link matches")
            return None
        if tweet.attachments:
            # potentially already has screenshot (this conditional could be subject to change)
            logger.debug(f"tweet: {tweet} -- tweet has attachments")
            return None
        items = [Item(inspect_link=match.group()) for match in matches]
        items_tweet = ItemsTweet(tweet.data)
        items_tweet.assign_items(*items)
        for item in items:
            item._tweet = items_tweet
        items_tweet._twitter = self
        return items_tweet

    def find_tweets(self) -> list[ItemsTweet]:
        search_results: tweepy.Response = self.search_recent_tweets(
            query=INSPECT_LINK_QUERY,
            expansions=self.TWEET_EXPANSIONS,
            tweet_fields=self.TWEET_TWEET_FIELDS,
            user_fields=self.TWEET_USER_FIELDS,
        )
        tweets: list[tweepy.Tweet] = search_results.data
        items_tweets: list[ItemsTweet] = []
        for tweet in tweets:
            items_tweet = self._tweet_to_items_tweet(tweet)
            if not items_tweet:
                continue
            items_tweets.append(items_tweet)
        return items_tweets

    def _start(self):

        self._live_twitter.filter(
            expansions=self.TWEET_EXPANSIONS,
            tweet_fields=self.TWEET_TWEET_FIELDS,
            user_fields=self.TWEET_USER_FIELDS,
            threaded=True
        )

    def media_upload(self, filename, *, file=None, chunked=False,
                     media_category=None, additional_owners=None, **kwargs) -> tweepy.models.Media:
        return self._twitter_v1.media_upload(filename=filename, file=file, chunked=chunked,
                                             media_category=media_category, additional_owners=additional_owners, **kwargs)
