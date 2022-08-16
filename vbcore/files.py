import os
import tempfile
import typing as t
from dataclasses import dataclass

try:
    from chardet import UniversalDetector as Detector
except ImportError:
    Detector = None  # type: ignore


OptStr = t.Optional[str]


@dataclass(frozen=True)
class EncodingData:
    confidence: float
    encoding: t.Optional[str]
    language: t.Optional[str] = None


class VBEncodingError(Exception):
    def __init__(
        self,
        filename: str,
        encoding: t.Optional[str],
        supported: t.List[str],
        confidence: t.Optional[float] = None,
        language: t.Optional[str] = None,
    ):
        self.filename = filename
        self.encoding = encoding
        self.language = language
        self.supported = supported
        self.confidence = confidence

        prefix = f"error while detecting encoding for file '{filename}':"
        extra = (
            f"(confidence: {confidence}, language: {language})"
            if language
            else f"(confidence: {confidence})"
        )
        suffix = f"\nSupported encodings are {tuple(supported)}"
        if encoding:
            super().__init__(
                f"{prefix} file encoding '{encoding}' {extra} not supported!{suffix}"
            )
        else:
            super().__init__(
                f"{prefix} unable to detect file encoding {extra}!{suffix}"
            )


class FileHandler:
    def __init__(
        self,
        filename: OptStr = None,
        encoding: OptStr = None,
        supporter_encodings: t.Sequence[str] = (),
    ):
        self.filename = filename
        self.encoding = encoding or "utf-8"
        self.supporter_encodings = supporter_encodings

    def open(self, filename: OptStr = None, **kwargs):
        encoding = kwargs.pop("encoding", self.encoding)
        return open(filename or self.filename, encoding=encoding, **kwargs)

    def num_lines(self, filename: OptStr = None) -> int:
        with self.open(filename) as file:
            return sum(1 for _ in file)

    @classmethod
    def skip(cls, file: t.IO, lines: int):
        for _ in range(0, lines):
            try:
                next(file)
            except StopIteration:
                return

    def read_text(self, filename: OptStr = None, **kwargs) -> str:
        with self.open(filename, **kwargs) as file:
            return file.read()

    @classmethod
    def detect_encoding(cls, filename: str) -> EncodingData:
        assert Detector is not None, "'chardet' required, install it!"
        detector = Detector()
        with open(filename, "rb") as file:
            for line in file:
                detector.feed(line)
                if detector.done:
                    break
            detector.close()

        return EncodingData(**detector.result)

    def check_encoding(self, filename: str, *extra_supported):
        encoding = self.detect_encoding(filename)
        supported_encodings = [
            self.encoding,
            *self.supporter_encodings,
            *extra_supported,
        ]
        if encoding.encoding not in supported_encodings:
            raise VBEncodingError(
                filename,
                encoding.encoding,
                supported_encodings,
                confidence=encoding.confidence,
                language=encoding.language,
            )


class TempFile:
    def __init__(self, data):
        self.data = data
        # pylint: disable=consider-using-with
        self.file = tempfile.NamedTemporaryFile(delete=False)

    def __enter__(self):
        self.file.write(self.data)
        self.file.close()
        return self.file

    def __exit__(self, exc_type, exc_value, exc_traceback):
        os.unlink(self.file.name)
