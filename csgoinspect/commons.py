from __future__ import annotations

import os
import re

import tweepy

LIVE_RULES = [
    tweepy.StreamRule('"+csgo_econ_action_preview"', tag="+csgo_econ_action_preview'"),
    tweepy.StreamRule('"steam://rungame/730"', tag="steam://rungame/730"),
]
INSPECT_LINK_QUERY = '"steam://rungame/730" OR "+csgo_econ_action_preview"'
INSPECT_URL_REGEX = re.compile(
    "(steam://rungame/730/[0-9]+/(?:\\+| )csgo_econ_action_preview(?:%20| ))(?:(?P<S>S[0-9]+)|(?P<M>M[0-9]+))(?P<A>A[0-9]+)(?P<D>D[0-9]+)"
)

TWEET_EXPANSIONS = ["referenced_tweets.id", "author_id", "referenced_tweets.id.author_id", "attachments.media_keys"]
TWEET_TWEET_FIELDS = ["id", "text", "attachments"]
TWEET_USER_FIELDS = ["id", "name", "username"]

TWITTER_BEARER_TOKEN = os.environ["TWITTER_BEARER_TOKEN"]
TWITTER_API_KEY = os.environ["TWITTER_API_KEY"]
TWITTER_API_KEY_SECRET = os.environ["TWITTER_API_KEY_SECRET"]
TWITTER_ACCESS_TOKEN = os.environ["TWITTER_ACCESS_TOKEN"]
TWITTER_ACCESS_TOKEN_SECRET = os.environ["TWITTER_ACCESS_TOKEN_SECRET"]

REDIS_HOST = os.environ["REDIS_HOST"]
REDIS_PASSWORD = os.environ["REDIS_PASSWORD"]
REDIS_PORT = int(os.environ["REDIS_PORT"])
REDIS_DATABASE = int(os.environ["REDIS_DATABASE"])
REDIS_EX = 60 * 60 * 24 * 30
