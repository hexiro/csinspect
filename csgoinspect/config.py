from __future__ import annotations

import os
import pathlib
import re

import dotenv
import tweepy


# --- paths ---
PARENT_DIRECTORY = pathlib.Path(__file__).parents[1]
DOTENV_PATH = PARENT_DIRECTORY / ".env"
if DOTENV_PATH.is_file():
    dotenv.load_dotenv(DOTENV_PATH)

# --- meta ---
IS_DEV = os.getenv("IS_DEV", "false").lower() == "true"
ONLY_RESPOND_TO_DEV = IS_DEV and os.getenv("ONLY_RESPOND_TO_DEV", "false").lower() == "true"
DEV_DONT_SEND_TWEETS = IS_DEV and os.getenv("DEV_DONT_SEND_TWEETS", "false").lower() == "true"
DEV_ID = int(os.environ["DEV_ID"]) if ONLY_RESPOND_TO_DEV else None
MAX_FAILED_ATTEMPTS = 5

# --- twitter ---
TWITTER_LIVE_RULES = [
    tweepy.StreamRule('"+csgo_econ_action_preview"', tag="+csgo_econ_action_preview'"),
    tweepy.StreamRule('"steam://rungame/730"', tag="steam://rungame/730"),
]
TWITTER_INSPECT_LINK_QUERY = '"steam://rungame/730" OR "+csgo_econ_action_preview"'
TWITTER_INSPECT_URL_REGEX = re.compile(
    "(steam://rungame/730/[0-9]+/(?:\\+| )csgo_econ_action_preview(?:%20| ))(?:(?P<S>S[0-9]+)|(?P<M>M[0-9]+))(?P<A>A[0-9]+)(?P<D>D[0-9]+)"
)

TWEET_EXPANSIONS = ["author_id", "attachments.media_keys"]
TWEET_TWEET_FIELDS = ["id", "text", "attachments", "conversation_id"]
TWEET_USER_FIELDS = ["id", "name", "username"]
TWITTER_MAX_IMAGES_PER_TWEET = 4

TWITTER_BEARER_TOKEN = os.environ["TWITTER_BEARER_TOKEN"]
TWITTER_API_KEY = os.environ["TWITTER_API_KEY"]
TWITTER_API_KEY_SECRET = os.environ["TWITTER_API_KEY_SECRET"]
TWITTER_ACCESS_TOKEN = os.environ["TWITTER_ACCESS_TOKEN"]
TWITTER_ACCESS_TOKEN_SECRET = os.environ["TWITTER_ACCESS_TOKEN_SECRET"]

# --- redis ---
REDIS_HOST = os.getenv("REDIS_HOST", default="localhost")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", default=None)
REDIS_PORT = int(os.getenv("REDIS_PORT", default=6379))
REDIS_DATABASE = int(os.getenv("REDIS_DATABASE", default=0))
REDIS_EX = 60 * 60 * 24 * 30

# --- sentry ---
SENTRY_DSN = os.getenv("SENTRY_DSN")
