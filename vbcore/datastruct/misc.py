import typing as t
from dataclasses import dataclass

from vbcore.base import BaseDTO


@dataclass
class GeoJsonPoint(BaseDTO):
    coordinates: t.List[float]
    type: str

    def __init__(self, lat: float = 0.0, lon: float = 0.0):
        self.type = "Point"
        self.coordinates = [lon, lat]
        self.lat = lat
        self.lon = lon
