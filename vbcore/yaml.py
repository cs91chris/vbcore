# based on:
# https://github.com/nameko/nameko/blob/a719cb1487f643769e2d13daf255c20551490f43/nameko/cli/main.py#L102-L111

import os
import re

import yaml

from .datastruct import ObjectDict
from .loggers import Log

ENV_VAR_MATCHER = re.compile(
    r"""
        \${        # match characters `${` literally
        ([^}:\s]+) # 1st group: matches any character except `}` or `:`
        :?         # matches the literal `:` character zero or one times
        ([^}]+)?   # 2nd group: matches any character except `}`
        }          # match character `}` literally
    """,
    re.VERBOSE,
)

IMPLICIT_ENV_VAR_MATCHER = re.compile(
    r"""
        .*      # matches any number of any characters
        \${.*}  # matches any number of any characters
                # between `${` and `}` literally
        .*      # matches any number of any characters
    """,
    re.VERBOSE,
)


def loads(data, loader=None, as_object: bool = True):
    data = yaml.load(data, Loader=loader or yaml.Loader)  # nosec
    if as_object:
        return ObjectDict.normalize(data)
    return data


def load_yaml_file(filename: str, encoding: str = "utf-8", **kwargs):
    with open(filename, encoding=encoding) as f:
        return loads(f, **kwargs)


def load_optional_yaml_file(filename: str, default=None, **kwargs):
    try:
        return load_yaml_file(filename, **kwargs)
    except OSError as exc:
        Log.get(__name__).warning(exc, exc_info=True)
        return ObjectDict() if default is None else default


def _replace_env_var(match):
    env_var, default = match.groups()
    value = os.environ.get(env_var, None)
    if value is None:
        if default is None:
            # regex module return None instead of ''
            # if engine did not enter default capture group
            default = ""

        value = default
        while IMPLICIT_ENV_VAR_MATCHER.match(value):
            value = ENV_VAR_MATCHER.sub(_replace_env_var, value)
    return value


def _constructor_env_var(loader, node, raw: bool = False):
    raw_value = loader.construct_scalar(node)
    value = ENV_VAR_MATCHER.sub(_replace_env_var, raw_value)
    return value if raw else loads(value, loader.__class__, as_object=False)


def _constructor_raw_env_var(loader, node):
    return _constructor_env_var(loader, node, raw=True)


def _constructor_include(loader, node):
    return load_yaml_file(node.value, loader=loader.__class__)


def _constructor_optional_include(loader, node):
    return load_optional_yaml_file(node.value, loader=loader.__class__)


yaml.add_constructor("!include", _constructor_include)
yaml.add_constructor("!opt_include", _constructor_optional_include)
yaml.add_constructor("!env_var", _constructor_env_var)
yaml.add_constructor("!raw_env_var", _constructor_raw_env_var)
yaml.add_implicit_resolver("!env_var", IMPLICIT_ENV_VAR_MATCHER)
