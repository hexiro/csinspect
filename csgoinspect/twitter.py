from __future__ import annotations

import os
import re
from collections import defaultdict
from typing import TYPE_CHECKING

import tweepy

from csgoinspect import commons
from csgoinspect.exceptions import InvalidTweetError
from csgoinspect.item import Item
from csgoinspect.tweet import Tweet

if TYPE_CHECKING:
    import tweepy.models


class Twitter:
    """A wrapper class around tweepy to simplify Twitter API interactions."""

    TWITTER_API_KEY = os.environ["TWITTER_API_KEY"]
    TWITTER_API_KEY_SECRET = os.environ["TWITTER_API_KEY_SECRET"]
    TWITTER_ACCESS_TOKEN = os.environ["TWITTER_ACCESS_TOKEN"]
    TWITTER_ACCESS_TOKEN_SECRET = os.environ["TWITTER_ACCESS_TOKEN_SECRET"]

    def __init__(self):
        authentication = tweepy.OAuthHandler(self.TWITTER_API_KEY, self.TWITTER_API_KEY_SECRET)
        authentication.set_access_token(self.TWITTER_ACCESS_TOKEN, self.TWITTER_ACCESS_TOKEN_SECRET)
        self._twitter = tweepy.API(authentication)

    def fetch_tweets(self) -> list[Tweet]:
        tweets: list[Tweet] = []
        search_results: tweepy.models.SearchResults = self._twitter.search_tweets(
            q=commons.INSPECT_LINK_QUERY,
            result_type="recent",
            count=100,
            tweet_mode="extended",
        )
        status: tweepy.models.Status
        for status in search_results:
            try:
                text: str = status.full_text
                _id = status.id
            except AttributeError as e:
                raise InvalidTweetError("Twitter Status does not posses the valid attributes neeeded.") from e

            # Twitter only allows 4 images
            matches: list[re.Match] = list(commons.INSPECT_URL_REGEX.finditer(text))
            matches = matches[:4]

            items = [Item(inspect_link=match.group()) for match in matches]
            tweet = Tweet(id=_id, text=text, items=items)
            for item in items:
                item._tweet = tweet
            tweets.append(tweet)

        return tweets