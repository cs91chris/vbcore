import enum

from vbcore.base import BaseDTO
from vbcore.data.transformations.builders.base import Builder
from vbcore.data.transformations.builders.csv import CSVBuilder, CSVBuilderOptions
from vbcore.data.transformations.builders.html import HTMLBuilder, HTMLBuilderOptions
from vbcore.data.transformations.builders.json import JSONBuilder, JSONBuilderOptions
from vbcore.data.transformations.builders.xml import XMLBuilder, XMLBuilderOptions
from vbcore.data.transformations.builders.yaml import YAMLBuilder, YAMLBuilderOptions
from vbcore.factory import ItemEnumMeta, ItemEnumMixin, ItemFactory


class BuilderEnum(
    ItemEnumMixin[BaseDTO],
    enum.Enum,
    metaclass=ItemEnumMeta,
):
    JSON = JSONBuilder, JSONBuilderOptions
    XML = XMLBuilder, XMLBuilderOptions
    YAML = YAMLBuilder, YAMLBuilderOptions
    CSV = CSVBuilder, CSVBuilderOptions
    HTML = HTMLBuilder, HTMLBuilderOptions


class BuilderFactory(ItemFactory[BuilderEnum, Builder]):
    items = BuilderEnum
