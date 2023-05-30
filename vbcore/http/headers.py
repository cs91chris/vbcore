import enum

from vbcore.enums import IStrEnum, LStrEnum, StrEnum


class TypeEnum(LStrEnum):
    APPLICATION = enum.auto()
    AUDIO = enum.auto()
    IMAGE = enum.auto()
    TEXT = enum.auto()
    VIDEO = enum.auto()


class ContentTypeEnum(StrEnum):
    CSS = f"{TypeEnum.TEXT}/css"
    CSV = f"{TypeEnum.TEXT}/csv"
    HTML = f"{TypeEnum.TEXT}/html"
    PLAIN = f"{TypeEnum.TEXT}/plain"
    EXCEL = f"{TypeEnum.APPLICATION}/vnd.ms-excel"
    BASE64 = f"{TypeEnum.APPLICATION}/base64"
    YAML = f"{TypeEnum.APPLICATION}/yaml"
    JS = f"{TypeEnum.APPLICATION}/javascript"
    JAR = f"{TypeEnum.APPLICATION}/java-archive"
    JSON = f"{TypeEnum.APPLICATION}/json"
    PDF = f"{TypeEnum.APPLICATION}/pdf"
    STREAM = f"{TypeEnum.APPLICATION}/octet-stream"
    XML = f"{TypeEnum.APPLICATION}/xml"
    ZIP = f"{TypeEnum.APPLICATION}/zip"
    TAR = f"{TypeEnum.APPLICATION}/x-tar"
    JPEG = f"{TypeEnum.IMAGE}/jpeg"
    PNG = f"{TypeEnum.IMAGE}/png"
    SVG = f"{TypeEnum.IMAGE}/svg+xml"
    WEBP = f"{TypeEnum.IMAGE}/webp"
    WAV = f"{TypeEnum.AUDIO}/wav"
    JSON_PROBLEM = f"{TypeEnum.APPLICATION}/problem+json"
    XML_PROBLEM = f"{TypeEnum.APPLICATION}/problem+xml"
    JSON_HEALTH = f"{TypeEnum.APPLICATION}/health+json"
    FORM_URLENCODED = f"{TypeEnum.APPLICATION}/x-www-form-urlencoded"
    FORM_DATA = "multipart/form-data"


class HeaderEnum(IStrEnum):
    def _generate_next_value_(self, *_):
        return self.lower().replace("_", "-")

    ACCEPT = enum.auto()
    ACCEPT_CHARSET = enum.auto()
    ACCEPT_DATETIME = enum.auto()
    ACCEPT_ENCODING = enum.auto()
    ACCEPT_LANGUAGE = enum.auto()
    ACCEPT_PATCH = enum.auto()
    ACCEPT_RANGES = enum.auto()
    ACCESS_CONTROL_ALLOW_ORIGIN = enum.auto()
    ACCESS_CONTROL_EXPOSE_HEADERS = enum.auto()
    ACCESS_CONTROL_REQUEST_HEADERS = enum.auto()
    ACCESS_CONTROL_REQUEST_METHOD = enum.auto()
    AGE = enum.auto()
    AUTHORIZATION = enum.auto()
    CACHE_CONTROL = enum.auto()
    CONTENT_DISPOSITION = enum.auto()
    CONTENT_ENCODING = enum.auto()
    CONTENT_LANGUAGE = enum.auto()
    CONTENT_LENGTH = enum.auto()
    CONTENT_LOCATION = enum.auto()
    CONTENT_RANGE = enum.auto()
    CONTENT_TYPE = enum.auto()
    COOKIE = enum.auto()
    DATE = enum.auto()
    ETAG = enum.auto()
    EXPIRES = enum.auto()
    IF_MATCH = enum.auto()
    IF_MODIFIED_SINCE = enum.auto()
    IF_NONE_MATCH = enum.auto()
    IF_RANGE = enum.auto()
    IF_UNMODIFIED_SINCE = enum.auto()
    LAST_MODIFIED = enum.auto()
    LINK = enum.auto()
    LOCATION = enum.auto()
    PROXY_AUTHENTICATE = enum.auto()
    PROXY_AUTHORIZATION = enum.auto()
    RANGE = enum.auto()
    REFERER = enum.auto()
    RETRY_AFTER = enum.auto()
    SET_COOKIE = enum.auto()
    STRICT_TRANSPORT_SECURITY = enum.auto()
    TRANSFER_ENCODING = enum.auto()
    USER_AGENT = enum.auto()
    WWW_AUTHENTICATE = enum.auto()
    X_REQUEST_ID = enum.auto()
    X_ACCEL_CHARSET = enum.auto()
    X_ACCEL_BUFFERING = enum.auto()
    X_ACCEL_EXPIRES = enum.auto()
    X_ACCEL_LIMIT_RATE = enum.auto()
    X_ACCEL_REDIRECT = enum.auto()
    X_API_VERSION = enum.auto()
    X_PAGINATION_COUNT = enum.auto()
    X_PAGINATION_NUM_PAGES = enum.auto()
    X_PAGINATION_PAGE = enum.auto()
    X_PAGINATION_PAGE_SIZE = enum.auto()
    X_RATELIMIT_LIMIT = enum.auto()
    X_RATELIMIT_RESET = enum.auto()
    X_RATELIMIT_REMAINING = enum.auto()
