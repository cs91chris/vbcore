from typing import Any, Callable, Mapping, Optional, TypeVar

from vbcore.lambdas import identity

T = TypeVar("T", bound=Mapping)


def map_keys(data: T, mapper: Optional[Callable[[Any], Any]] = None, **kwargs) -> T:
    def _map(k: Any) -> Any:
        t = mapper or identity
        return kwargs.get(k, t(k))

    mapped = data.__class__()

    for key in data:
        mapped[_map(key)] = data[key]  # type: ignore[index]

    return mapped
