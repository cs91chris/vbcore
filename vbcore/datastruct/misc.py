import typing as t
from dataclasses import dataclass

from vbcore.base import BaseDTO


@dataclass(frozen=True, kw_only=True)
class GeoJsonPoint(BaseDTO):
    type: str = "Point"
    lat: float = 0.0
    lon: float = 0.0

    @property
    def coordinates(self) -> t.List[float]:
        return [self.lon, self.lat]

    def to_dict(self, *_, **__) -> dict:
        return {"type": self.type, "coordinates": self.coordinates}
