import os
import tempfile
import typing as t
from dataclasses import dataclass

from vbcore.datastruct.lazy import LazyImporter
from vbcore.exceptions import VBException
from vbcore.types import OptStr

Detector = LazyImporter.do_import(
    "chardet:UniversalDetector",
    message="'chardet' required, install it!",
)


@dataclass(frozen=True)
class EncodingData:
    confidence: float
    encoding: OptStr
    language: OptStr = None


class VBEncodingError(VBException):
    def __init__(
        self,
        filename: str,
        encoding: OptStr,
        supported: t.List[str],
        confidence: t.Optional[float] = None,
        language: OptStr = None,
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
        supported_encodings: t.Sequence[str] = (),
    ):
        self.filename = filename
        self.encoding = encoding or "utf-8"
        self.supported_encodings = supported_encodings

    def open(self, filename: OptStr = None, **kwargs) -> t.IO:
        encoding = kwargs.pop("encoding", self.encoding)
        return open(filename or self.filename, encoding=encoding, **kwargs)

    def open_binary(self, filename: OptStr = None, **kwargs) -> t.IO:
        return open(filename or self.filename, mode="rb", **kwargs)

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

    def detect_encoding(self, filename: OptStr = None) -> EncodingData:
        detector = Detector()
        with self.open_binary(filename) as file:
            for line in file:
                detector.feed(line)
                if detector.done:
                    break
            detector.close()

        return EncodingData(**detector.result)

    def check_encoding(
        self, filename: OptStr = None, extra_supported: t.Sequence[str] = ()
    ):
        encoding = self.detect_encoding(filename)
        supported_encodings = [
            self.encoding,
            *self.supported_encodings,
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
