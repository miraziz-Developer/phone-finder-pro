from enum import StrEnum


class UseCase(StrEnum):
    GAMING = "gaming"
    PHOTOGRAPHY = "photography"
    BUSINESS = "business"
    DAILY_USE = "daily_use"
    CONTENT_CREATION = "content_creation"


class BrandName(StrEnum):
    APPLE = "apple"
    SAMSUNG = "samsung"
    XIAOMI = "xiaomi"
    GOOGLE = "google"
    NOTHING = "nothing"
    NO_PREFERENCE = "no_preference"


class PhoneSortOrder(StrEnum):
    PRICE_ASC = "price_asc"
    PRICE_DESC = "price_desc"
    NEWEST = "newest"
    POPULAR = "popular"
    SCORE = "score"
