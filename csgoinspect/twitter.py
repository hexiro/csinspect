from __future__ import annotations

import time
from typing import re

import tweepy.models

from csgoinspect.commons import TWITTER_BEARER_TOKEN, TWITTER_API_KEY, TWITTER_API_KEY_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET, \
    INSPECT_URL_REGEX
from csgoinspect.item import Item
from csgoinspect.tweet import ItemsTweet


class Twitter(tweepy.Client):
    """Merged wrapper of v1, v2, and Streaming APIs provided by Tweepy."""
    rules = [
        tweepy.StreamRule('"+csgo_econ_action_preview"', tag="+csgo_econ_action_preview'"),
        tweepy.StreamRule('"steam://rungame/730"', tag="steam://rungame/730"),
    ]

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
        self._live_twitter.add_rules(self.rules)
        self._live_twitter.on_tweet = self.on_tweet
        self._live_twitter.on_connect = self.on_connect
        self._live_twitter.on_disconnect = self.on_disconnect

    def on_tweet(self, tweet: tweepy.Tweet):
        print(f"{tweet=}")
        # Twitter only allows 4 images
        matches: list[re.Match] = list(INSPECT_URL_REGEX.finditer(tweet.text))
        matches = matches[:4]
        if not matches:
            return
        items = [Item(inspect_link=match.group()) for match in matches]
        items_tweet = ItemsTweet(tweet.data)
        items_tweet.assign_items(*items)
        for item in items:
            item._tweet = items_tweet
        items_tweet._twitter = self
        self._items_tweets.append(items_tweet)

    def on_connect(self):
        print("connected!")

    def on_disconnect(self):
        print("disconnected :(")

    def live(self):
        if not self._live_twitter.running:
            self._start()
        while True:
            if self._items_tweets:
                yield self._items_tweets.pop(0)
            time.sleep(1)

    def _start(self):
        expansions = ["referenced_tweets.id", "author_id", "referenced_tweets.id.author_id", "attachments.media_keys"]
        tweet_fields = ["id", "text", "attachments"]
        user_fields = ["id", "name", "username"]

        self._live_twitter.filter(
            expansions=expansions,
            tweet_fields=tweet_fields,
            user_fields=user_fields,
            threaded=True
        )

    def media_upload(self, filename, *, file=None, chunked=False,
                     media_category=None, additional_owners=None, **kwargs) -> tweepy.models.Media:
        return self._twitter_v1.media_upload(filename=filename, file=file, chunked=chunked,
                                             media_category=media_category, additional_owners=additional_owners, **kwargs)
