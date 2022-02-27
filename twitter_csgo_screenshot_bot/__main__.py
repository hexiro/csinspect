from __future__ import annotations

import io
import os
import pathlib
from typing import TYPE_CHECKING

import dotenv
import regex
import requests
from redis import Redis
from twython import Twython

from twitter_csgo_screenshot_bot import swapgg

if TYPE_CHECKING:
    from twitter_csgo_screenshot_bot.datatypes import SearchResults, SearchItem

dotenv_path = pathlib.Path(__file__).parents[1] / ".env"
dotenv.load_dotenv(dotenv_path)

redis = Redis(
    host=os.environ["REDIS_HOST"],
    password=os.environ["REDIS_PASSWORD"],
    port=int(os.environ["REDIS_PORT"]),
    db=int(os.environ["REDIS_DATABASE"])
)

APP_KEY = os.environ["TWITTER_API_KEY"]
APP_SECRET = os.environ["TWITTER_API_KEY_SECRET"]

OAUTH_TOKEN = redis.get("TWITTER_OAUTH_TOKEN")
OAUTH_TOKEN_SECRET = redis.get("TWITTER_OAUTH_TOKEN_SECRET")

twitter = Twython(app_key=APP_KEY, app_secret=APP_SECRET,
                  oauth_token=OAUTH_TOKEN, oauth_token_secret=OAUTH_TOKEN_SECRET)

INSPECT_LINK_QUERY = '"steam://rungame/730" "+csgo_econ_action_preview"'
INSPECT_URL_REGEX = regex.compile(
    r"(steam:\/\/rungame\/730\/[0-9]+\/\+csgo_econ_action_preview%20((?<S>S[0-9]+)|(?<M>M[0-9]+)))(?<A>A[0-9]+)(?<D>D[0-9]+)")


def already_has_screenshot(tweet: SearchItem) -> bool:
    try:
        if tweet["extended_entities"]["media"]:
            return True
    except KeyError:
        pass
    return False


def already_responded(tweet: SearchItem) -> bool:
    try:
        status_id = tweet["id_str"]
    except KeyError:
        return True
    return redis.get(status_id) is not None


def main() -> None:
    search_results: SearchResults = twitter.search(q=INSPECT_LINK_QUERY, result_type="recent", count=100,
                                                   tweet_mode="extended")

    tweets: dict[str, SearchItem] = {}

    for tweet in search_results["statuses"]:
        if already_has_screenshot(tweet):
            continue
        print(f"{already_responded(tweet)=}")
        if already_responded(tweet):
            continue
        text = tweet["full_text"]
        match: regex.Match = INSPECT_URL_REGEX.search(text)
        if not match:
            continue

        inspect_link: str = match.group()
        tweets[inspect_link] = tweet
        swapgg.take_screenshot(inspect_link)

    for inspect_link, tweet in tweets.items():
        image_link = swapgg.wait_for_screenshot(inspect_link)
        print(f"{image_link=} {inspect_link=}")
        if not image_link:
            continue

        status_id = tweet["id_str"]
        screen_name = tweet["user"]["screen_name"]

        if not status_id or not screen_name:
            continue

        screenshot = requests.get(image_link)
        screenshot_file = io.BytesIO(screenshot.content)
        media = twitter.upload_media(media=screenshot_file)
        print(tweet)

        redis.set(name=status_id, value=image_link, ex=60 * 60 * 24 * 7)
        twitter.update_status(status=f"@{screen_name}",
                              in_reply_to_status_id=status_id, media_ids=[media["media_id"]])
    swapgg.sio.disconnect()


if __name__ == "__main__":
    main()
