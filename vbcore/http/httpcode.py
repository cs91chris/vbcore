import enum
import typing as t

CONTINUE = 100
SWITCHING_PROTOCOL = 101
PROCESSING = 102  # WebDAV
EARLY_HINTS = 103
SUCCESS = 200
CREATED = 201
ACCEPTED = 202
NON_AUTHORITATIVE_INFORMATION = 203
NO_CONTENT = 204
RESET_CONTENT = 205
PARTIAL_CONTENT = 206
MULTI_STATUS = 207  # WebDAV
ALREADY_REPORTED = 208  # WebDAV
IM_USED = 226
MULTIPLE_CHOICES = 300
MOVED_PERMANENTLY = 301
FOUND = 302
SEE_OTHER = 303
NOT_MODIFIED = 304
USE_PROXY = 305
RESERVED = 306
TEMPORARY_REDIRECT = 307
PERMANENT_REDIRECT = 308
BAD_REQUEST = 400
UNAUTHORIZED = 401
PAYMENT_REQUIRED = 402
FORBIDDEN = 403
NOT_FOUND = 404
METHOD_NOT_ALLOWED = 405
NOT_ACCEPTABLE = 406
PROXY_AUTHENTICATION_REQUIRED = 407
REQUEST_TIMEOUT = 408
CONFLICT = 409
GONE = 410
LENGTH_REQUIRED = 411
PRECONDITION_FAILED = 412
REQUEST_ENTITY_TOO_LARGE = 413
REQUEST_URI_TOO_LONG = 414
UNSUPPORTED_MEDIA_TYPE = 415
RANGE_NOT_SATISFIABLE = 416
EXPECTATION_FAILED = 417
IM_A_TEAPOT = 418
MISDIRECTED_REQUEST = 421
UNPROCESSABLE_ENTITY = 422
LOCKED = 423
FAILED_DEPENDENCY = 424  # WebDAV
TOO_EARLY = 425
UPGRADE_REQUIRED = 426
PRECONDITION_REQUIRED = 428
TOO_MANY_REQUESTS = 429
REQUEST_HEADER_FIELDS_TOO_LARGE = 431
NO_RESPONSE = 444  # nginx
UNAVAILABLE_FOR_LEGAL_REASON = 451
INTERNAL_SERVER_ERROR = 500
NOT_IMPLEMENTED = 501
BAD_GATEWAY = 502
SERVICE_UNAVAILABLE = 503
GATEWAY_TIMEOUT = 504
HTTP_VERSION_NOT_SUPPORTED = 505
INSUFFICIENT_STORAGE = 507  # WebDAV
LOOP_DETECTED = 508  # WebDAV
BANDWIDTH_LIMIT = 509  # apache
NOT_EXTENDED = 510
NETWORK_AUTHENTICATION_REQUIRED = 511
UNKNOWN_ERROR = 520  # cloudflare

IntStatusType = t.Union[int, "StatusType"]


class StatusType(enum.IntEnum):
    INFORMATIONAL = 1
    SUCCESS = 2
    REDIRECTION = 3
    CLIENT_ERROR = 4
    SERVER_ERROR = 5

    @classmethod
    def _missing_(cls, value) -> "StatusType":
        if isinstance(value, int):
            return cls(value // 100)
        return cls(value)


def is_informational(s: IntStatusType) -> bool:
    return StatusType(s) == StatusType.INFORMATIONAL


def is_success(s: IntStatusType) -> bool:
    return StatusType(s) == StatusType.SUCCESS


def is_redirection(s: IntStatusType) -> bool:
    return StatusType(s) == StatusType.REDIRECTION


def is_client_error(s: IntStatusType) -> bool:
    return StatusType(s) == StatusType.CLIENT_ERROR


def is_server_error(s: IntStatusType) -> bool:
    return StatusType(s) == StatusType.SERVER_ERROR


def is_ok(s: IntStatusType) -> bool:
    return StatusType(s) in (
        StatusType.INFORMATIONAL,
        StatusType.SUCCESS,
        StatusType.REDIRECTION,
    )


def is_ko(s: IntStatusType) -> bool:
    return not is_ok(s)
