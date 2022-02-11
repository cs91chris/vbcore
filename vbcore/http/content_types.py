import enum

from vbcore.datastruct import IStrEnum, StrEnum


class Types(IStrEnum):
    APPLICATION = enum.auto()
    AUDIO = enum.auto()
    IMAGE = enum.auto()
    TEXT = enum.auto()
    VIDEO = enum.auto()


class ContentType(StrEnum):
    CSS = f"{Types.TEXT}/css"
    CSV = f"{Types.TEXT}/csv"
    HTML = f"{Types.TEXT}/html"
    PLAIN = f"{Types.TEXT}/plain"
    EXCEL = f"{Types.APPLICATION}/vnd.ms-excel"
    JAR = f"{Types.APPLICATION}/java-archive"
    JSON = f"{Types.APPLICATION}/json"
    PDF = f"{Types.APPLICATION}/pdf"
    STREAM = f"{Types.APPLICATION}/octet-stream"
    XML = f"{Types.APPLICATION}/xml"
    ZIP = f"{Types.APPLICATION}/zip"
    TAR = f"{Types.APPLICATION}/x-tar"
    JPEG = f"{Types.IMAGE}/jpeg"
    PNG = f"{Types.IMAGE}/png"
    SVG = f"{Types.IMAGE}/svg+xml"
    WEBP = f"{Types.IMAGE}/webp"
    WAV = f"{Types.AUDIO}/wav"

    @classmethod
    def parse(cls, content_type: str) -> "ContentType":
        return cls(content_type)
