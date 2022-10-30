from __future__ import annotations

import os
import pathlib
import re

import dotenv
import tweepy

PARENT_DIRECTORY = pathlib.Path(__file__).parents[1]
DOTENV_PATH = PARENT_DIRECTORY / ".env"

if DOTENV_PATH.is_file():
    dotenv.load_dotenv(DOTENV_PATH)


IS_DEV = os.getenv("IS_DEV", "false").lower() == "true"
DEV_ID = int(os.environ["DEV_ID"]) if IS_DEV else None

SKINPORT_ID = 973912423295078400
PREFER_SKINPORT = IS_DEV and os.getenv("PREFER_SKINPORT", "false").lower() == "true"

MAX_FAILED_ATTEMPTS = 5

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

REDIS_HOST = os.getenv("REDIS_HOST", default="localhost")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", default=None)
REDIS_PORT = int(os.getenv("REDIS_PORT", default=6379))
REDIS_DATABASE = int(os.getenv("REDIS_DATABASE", default=0))
REDIS_EX = 60 * 60 * 24 * 30

SENTRY_DSN = os.getenv("SENTRY_DSN")
