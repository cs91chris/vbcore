import io
import typing as t
from functools import partial

from vbcore import json
from vbcore.datastruct import ObjectDict
from vbcore.http.client import HTTPClient

try:
    import jsonschema as json_schema
except ImportError as _exc:
    raise ImportError("you must install 'jsonschema'") from _exc

SchemaError = (json_schema.ValidationError, json_schema.SchemaError)


class JSONSchema:
    service = json_schema
    schema_error = SchemaError

    loader = partial(json.loads)
    dumper = partial(json.dumps, indent=4)
    marker = "3fb539deef7c4e2991f265c0a982f5ea"
    message_format = "{message}\nError in line {line}:\n{report}\n{message}"

    @classmethod
    def load_from_url(cls, url: str) -> dict:
        """

        :param url:
        :return:
        """
        res = HTTPClient(url, raise_on_exc=True).get(url)
        return res.body

    @classmethod
    def load_from_file(cls, file: str, encoding: str = "utf-8", **kwargs) -> dict:
        """

        :param file:
        :param encoding:
        :return:
        """
        if file.startswith("file://"):
            file = file[7:]

        with open(file, encoding=encoding, **kwargs) as f:
            return cls.loader(f.read())

    @classmethod
    def validate(
        cls,
        data: dict,
        schema: t.Union[dict, str],
        raise_exc: bool = False,
        checker=None,
    ) -> bool:
        """

        :param data:
        :param schema:
        :param raise_exc:
        :param checker:
        :return:
        """
        assert cls.service != ObjectDict, "you must install 'jsonschema'"

        if isinstance(schema, str):
            if schema.startswith("https://") or schema.startswith("http://"):
                schema = cls.load_from_url(schema)
            elif schema.startswith("file://"):
                schema = cls.load_from_file(schema)

        try:
            checker = checker or cls.service.FormatChecker()
            cls.service.validate(data, schema, format_checker=checker)
        except cls.schema_error as exc:
            if raise_exc is True:
                raise ValueError(cls.error_report(exc, data)) from exc
            return False
        return True

    @classmethod
    def error_report(
        cls, e, json_object: dict, lines_before: int = 8, lines_after: int = 8
    ):
        """
        From: https://github.com/ccpgames/jsonschema-errorprinter/blob/master/jsonschemaerror.py

        Generate a detailed report of a schema validation error.
        'e' is a jsonschema.ValidationError exception raised on 'json_object'.

        Steps to discover the location of the validation error:
            1. Traverse the json object using the 'path' in the validation exception
               and replace the offending value with a special marker.
            2. Pretty-print the json object indented json text.
            3. Search for the special marker in the json text to find the actual
               line number of the error.
            4. Make a report by showing the error line with a context of
               'lines_before' and 'lines_after' number of lines on each side.
        """
        if not e.path:
            return e.message or str(e)

        # Find the object that ha errors, and replace it with the marker.
        for entry in list(e.path)[:-1]:
            json_object = json_object[entry]

        if isinstance(json_object, dict):
            orig, json_object[e.path[-1]] = json_object[e.path[-1]], cls.marker
        else:
            orig = json_object

        # Pretty print the object and search for the marker.
        json_error = cls.dumper(json_object)
        err_line = None

        for lineno, text in enumerate(io.StringIO(json_error)):
            if cls.marker in text:
                err_line = lineno
                break

        if not err_line:
            return e.message or str(e)

        report = []
        json_object[e.path[-1]] = orig
        json_error = cls.dumper(json_object)

        for lineno, text in enumerate(io.StringIO(json_error)):
            # pylint: disable=consider-using-f-string
            line_text = "{:4}: {}".format(
                lineno + 1, ">" * 3 if lineno == err_line else " " * 3
            )
            report.append(line_text + text.rstrip("\n"))

        report = report[max(0, err_line - lines_before) : err_line + 1 + lines_after]
        return cls.message_format.format(
            line=err_line + 1, report="\n".join(report), message=e.message or str(e)
        )


class Fields:
    schema = ObjectDict(**{"$schema": "http://json-schema.org/draft-07/schema#"})

    null = ObjectDict(type="null")
    integer = ObjectDict(type="integer")
    string = ObjectDict(type="string")
    number = ObjectDict(type="number")
    boolean = ObjectDict(type="boolean")
    datetime = ObjectDict(type="string", format="date-time")
    any_object = ObjectDict(type="object", additionalProperties=True)
    any = ObjectDict(
        type=["integer", "string", "number", "boolean", "array", "object", "null"]
    )

    class Opt:
        integer = ObjectDict(type=["integer", "null"])
        string = ObjectDict(type=["string", "null"])
        number = ObjectDict(type=["number", "null"])
        boolean = ObjectDict(type=["boolean", "null"])

    @classmethod
    def oneof(cls, *args, **kwargs):
        return ObjectDict(oneOf=args if len(args) > 1 else (*args, cls.null), **kwargs)

    @classmethod
    def anyof(cls, *args, **kwargs):
        return ObjectDict(anyOf=args if len(args) > 1 else (*args, cls.null), **kwargs)

    @classmethod
    def ref(cls, path: str, **kwargs):
        return ObjectDict(**{"$ref": f"#{path}", **kwargs})

    @classmethod
    def enum(cls, *args, **kwargs):
        return {"enum": args, **kwargs}

    @classmethod
    def type(cls, *args, **kwargs):
        return {"type": args, **kwargs}

    @classmethod
    def object(
        cls,
        required=(),
        not_required=(),
        properties=None,
        all_required=True,
        additional=False,
        **kwargs,
    ):
        properties = properties or {}
        if not required and all_required is True:
            required = [i for i in properties.keys() if i not in not_required]

        return ObjectDict(
            type="object",
            additionalProperties=additional,
            required=required,
            properties=properties,
            **kwargs,
        )

    @classmethod
    def array(cls, items: dict, min_items: int = 0, **kwargs):
        return ObjectDict(type="array", minItems=min_items, items=items, **kwargs)

    @classmethod
    def array_object(cls, min_items: int = 0, **kwargs):
        return ObjectDict(type="array", minItems=min_items, items=cls.object(**kwargs))
