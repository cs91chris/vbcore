import typing as t
import uuid

from vbcore.types import OptStr


def get_uuid(
    ver: int = 4,
    hex_: bool = True,
    name: OptStr = None,
    ns: t.Optional[uuid.UUID] = None,
) -> t.Union[str, uuid.UUID]:
    if ver == 1:
        _uuid = uuid.uuid1()
    elif ver == 3:
        _uuid = uuid.uuid3(ns or uuid.NAMESPACE_DNS, name)
    elif ver == 4:
        _uuid = uuid.uuid4()
    elif ver == 5:
        _uuid = uuid.uuid5(ns or uuid.NAMESPACE_DNS, name)
    else:
        raise TypeError(f"invalid uuid version {ver}")

    return _uuid.hex if hex_ else _uuid


def check_uuid(
    u: t.Union[str, uuid.UUID],
    ver: int = 4,
    raise_exc: bool = False,
) -> bool:
    try:
        if isinstance(u, uuid.UUID):
            return True

        _uuid = uuid.UUID(u, version=ver)
        return u == (str(_uuid) if "-" in u else _uuid.hex)
    except (ValueError, TypeError, AttributeError) as exc:
        if raise_exc:
            raise ValueError(f"'{u}' is an invalid UUID{ver}") from exc
        return False
