import os
from collections import OrderedDict
from functools import partial

import decouple
from dotenv import load_dotenv as base_load_dotenv

_conf_search_path = os.environ.get("ENV_PATH")
_conf_file_name = os.environ.get("ENV_FILE")
_conf_file_encoding = os.environ.get("ENV_FILE_ENCODING") or "UTF-8"


class AutoConfig(decouple.AutoConfig):
    encoding = _conf_file_encoding

    SUPPORTED = OrderedDict(
        [
            (_conf_file_name or "settings.ini", decouple.RepositoryIni),
            (_conf_file_name or ".env", decouple.RepositoryEnv),
        ]
    )


config = AutoConfig(search_path=_conf_search_path or os.getcwd())

load_dotenv = partial(
    base_load_dotenv,
    dotenv_path=_conf_file_name,
    encoding=_conf_file_encoding,
)
