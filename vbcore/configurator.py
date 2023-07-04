import os
import typing as t
from collections import OrderedDict
from functools import partial

import decouple
from dotenv import load_dotenv as base_load_dotenv

from vbcore.types import OptAny

_conf_search_path = os.environ.get("ENV_PATH")
_conf_file_name = os.environ.get("ENV_FILE")
_conf_file_encoding = os.environ.get("ENV_FILE_ENCODING") or "UTF-8"


class AutoConfig(decouple.AutoConfig):
    encoding: str = _conf_file_encoding

    SUPPORTED: t.OrderedDict = OrderedDict(
        [
            (_conf_file_name or "settings.ini", decouple.RepositoryIni),
            (_conf_file_name or ".env", decouple.RepositoryEnv),
        ]
    )

    @classmethod
    def from_environ(
        cls,
        key: str,
        default: OptAny = None,
        required: bool = True,
        cast: t.Callable[[str], t.Any] = str,
    ) -> t.Any:
        env_var = os.environ.get(key)
        if env_var:
            try:
                return cast(env_var)
            except Exception as exc:
                raise ValueError(
                    f"unable to cast config key '{key}' to type: {cast}"
                ) from exc

        if required and not default:
            raise EnvironmentError(f"envvar '{key}' required or provide a default")

        return default


config = AutoConfig(search_path=_conf_search_path or os.getcwd())

load_dotenv = partial(
    base_load_dotenv,
    dotenv_path=_conf_file_name,
    encoding=_conf_file_encoding,
)
