from vbcore.datastruct import GeoJsonPoint
from vbcore.tester.asserter import Asserter


def test_geojson_point():
    Asserter.assert_equals(
        GeoJsonPoint(lon=1, lat=2).to_dict(),
        {"type": "Point", "coordinates": [1, 2]},
    )
