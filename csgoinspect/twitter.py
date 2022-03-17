from __future__ import annotations

import os
import re
from collections import defaultdict
from typing import TYPE_CHECKING

import tweepy

from csgoinspect.typings import InspectLink

if TYPE_CHECKING:
    import tweepy.models


class Twitter:
    """A wrapper class around tweepy to simplify Twitter API interactions."""

    TWITTER_API_KEY = os.environ["TWITTER_API_KEY"]
    TWITTER_API_KEY_SECRET = os.environ["TWITTER_API_KEY_SECRET"]
    TWITTER_ACCESS_TOKEN = os.environ["TWITTER_ACCESS_TOKEN"]
    TWITTER_ACCESS_TOKEN_SECRET = os.environ["TWITTER_ACCESS_TOKEN_SECRET"]

    INSPECT_LINK_QUERY = '"steam://rungame/730" "+csgo_econ_action_preview"'
    INSPECT_URL_REGEX = re.compile(
        "(steam://rungame/730/[0-9]+/(?:\\+| )csgo_econ_action_preview(?:%20| ))(?:(?P<S>S[0-9]+)|(?P<M>M[0-9]+))(?P<A>A[0-9]+)(?P<D>D[0-9]+)"
    )

    def __init__(self):
        authentication = tweepy.OAuthHandler(self.TWITTER_API_KEY, self.TWITTER_API_KEY_SECRET)
        authentication.set_access_token(self.TWITTER_ACCESS_TOKEN, self.TWITTER_ACCESS_TOKEN_SECRET)
        self._twitter = tweepy.API(authentication)

    def fetch_tweets(self) -> dict[tweepy.models.Status, list[InspectLink]]:
        inspect_link_tweets: dict[tweepy.models.Status, list[InspectLink]] = defaultdict(list)
        search_results: tweepy.models.SearchResults = self._twitter.search_tweets(
            q=self.INSPECT_LINK_QUERY,
            result_type="recent",
            count=100,
            tweet_mode="extended",
        )
        tweet: tweepy.models.Status
        for tweet in search_results:
            text: str = tweet.full_text

            # Twitter only allows 4 images
            matches: list[re.Match] = list(self.INSPECT_URL_REGEX.finditer(text))
            matches = matches[:4]

            for match in matches:
                inspect_link = InspectLink(match.group())
                inspect_link_tweets[tweet].append(inspect_link)
        return inspect_link_tweets
