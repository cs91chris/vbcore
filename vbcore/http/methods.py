import enum

from vbcore.enums import StrEnum


class HttpMethod(StrEnum):
    POST = enum.auto()
    PUT = enum.auto()
    GET = enum.auto()
    DELETE = enum.auto()
    PATCH = enum.auto()
    FETCH = enum.auto()
    HEAD = enum.auto()
    OPTIONS = enum.auto()


class WebDavMethod(StrEnum):
    COPY = enum.auto()
    LOCK = enum.auto()
    MKCOL = enum.auto()
    PROPFIND = enum.auto()
    PROPPATCH = enum.auto()
    UNLOCK = enum.auto()
