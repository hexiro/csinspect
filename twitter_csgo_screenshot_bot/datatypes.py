from __future__ import annotations

from typing import Optional, TypeAlias, TypedDict, Literal


class UserMentionsItem0(TypedDict):
    screen_name: str
    name: str
    id: int
    id_str: str
    indices: list[int]


class Entities(TypedDict):
    hashtags: list
    symbols: list
    user_mentions: list[UserMentionsItem0]
    urls: list


class Metadata(TypedDict):
    iso_language_code: str
    result_type: str


class UrlsItem0(TypedDict):
    url: str
    expanded_url: str
    display_url: str
    indices: list[int]


class Url(TypedDict):
    urls: list[UrlsItem0]


class Entities1(TypedDict):
    url: Url
    description: Url


class Entities2(TypedDict):
    description: Url


class User(TypedDict):
    id: int
    id_str: str
    name: str
    screen_name: str
    location: str
    description: str
    url: Optional[str]
    entities: Entities1 | Entities2
    protected: bool
    followers_count: int
    friends_count: int
    listed_count: int
    created_at: str
    favourites_count: int
    utc_offset: None
    time_zone: None
    geo_enabled: bool
    verified: bool
    statuses_count: int
    lang: None
    contributors_enabled: bool
    is_translator: bool
    is_translation_enabled: bool
    profile_background_color: str
    profile_background_image_url: Optional[str]
    profile_background_image_url_https: Optional[str]
    profile_background_tile: bool
    profile_image_url: str
    profile_image_url_https: str
    profile_banner_url: str
    profile_link_color: str
    profile_sidebar_border_color: str
    profile_sidebar_fill_color: str
    profile_text_color: str
    profile_use_background_image: bool
    has_extended_profile: bool
    default_profile: bool
    default_profile_image: bool
    following: bool
    follow_request_sent: bool
    notifications: bool
    translator_type: str
    withheld_in_countries: list


class StatusesItem0(TypedDict):
    created_at: str
    id: int
    id_str: str
    full_text: str
    truncated: bool
    display_text_range: list[int]
    entities: Entities
    metadata: Metadata
    source: str
    in_reply_to_status_id: int
    in_reply_to_status_id_str: str
    in_reply_to_user_id: int
    in_reply_to_user_id_str: str
    in_reply_to_screen_name: str
    user: User
    geo: None
    coordinates: None
    place: None
    contributors: None
    is_quote_status: bool
    retweet_count: int
    favorite_count: int
    favorited: bool
    retweeted: bool
    lang: str


class Large(TypedDict):
    w: int
    h: int
    resize: str


class Sizes(TypedDict):
    large: Large
    thumb: Large
    small: Large
    medium: Large


class MediaItem0(TypedDict):
    id: int
    id_str: str
    indices: list[int]
    media_url: str
    media_url_https: str
    url: str
    display_url: str
    expanded_url: str
    type: str
    sizes: Sizes


class Entities3(TypedDict):
    hashtags: list
    symbols: list
    user_mentions: list[UserMentionsItem0]
    urls: list
    media: list[MediaItem0]


class ExtendedEntities(TypedDict):
    media: list[MediaItem0]


class User1(TypedDict):
    id: int
    id_str: str
    name: str
    screen_name: str
    location: str
    description: str
    url: None
    entities: Entities2
    protected: bool
    followers_count: int
    friends_count: int
    listed_count: int
    created_at: str
    favourites_count: int
    utc_offset: None
    time_zone: None
    geo_enabled: bool
    verified: bool
    statuses_count: int
    lang: None
    contributors_enabled: bool
    is_translator: bool
    is_translation_enabled: bool
    profile_background_color: str
    profile_background_image_url: str
    profile_background_image_url_https: str
    profile_background_tile: bool
    profile_image_url: str
    profile_image_url_https: str
    profile_link_color: str
    profile_sidebar_border_color: str
    profile_sidebar_fill_color: str
    profile_text_color: str
    profile_use_background_image: bool
    has_extended_profile: bool
    default_profile: bool
    default_profile_image: bool
    following: bool
    follow_request_sent: bool
    notifications: bool
    translator_type: str
    withheld_in_countries: list


class StatusesItem12(TypedDict):
    created_at: str
    id: int
    id_str: str
    full_text: str
    truncated: bool
    display_text_range: list[int]
    entities: Entities3
    extended_entities: ExtendedEntities
    metadata: Metadata
    source: str
    in_reply_to_status_id: None
    in_reply_to_status_id_str: None
    in_reply_to_user_id: None
    in_reply_to_user_id_str: None
    in_reply_to_screen_name: None
    user: User1
    geo: None
    coordinates: None
    place: None
    contributors: None
    is_quote_status: bool
    retweet_count: int
    favorite_count: int
    favorited: bool
    retweeted: bool
    possibly_sensitive: bool
    lang: str


class SearchMetadata(TypedDict):
    completed_in: float
    max_id: int
    max_id_str: str
    next_results: str
    query: str
    refresh_url: str
    count: int
    since_id: int
    since_id_str: str


SearchItem: TypeAlias = StatusesItem0 | StatusesItem12


class SearchResults(TypedDict):
    statuses: list[SearchItem]
    search_metadata: SearchMetadata


class SwapGGScreenshotResponse(TypedDict):
    time: int
    status: str
    result: CompletedResult | NotCompletedResult;


class NotCompletedResult(TypedDict):
    marketName: str
    inspectLink: str
    state: str
    itemInfo: object  # typings not needed


class CompletedResult(TypedDict):
    marketName: str
    inspectLink: str
    state: Literal["COMPLETED"]
    itemInfo: object  # typings not needed
    imageLink: str


class ScreenshotReady(TypedDict):
    imageLink: str
    inspectLink: str
