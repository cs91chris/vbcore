from vbcore.jsonschema.support import Fields


class JSONRPC:
    REQUEST: dict = Fields.oneof(
        Fields.ref("/definitions/request", description="An individual request"),
        Fields.array(
            items=Fields.ref("/definitions/request"),
            description="An array of requests",
        ),
        **Fields.schema,
        description="A JSON RPC 2.0 request",
        definitions={
            "request": Fields.object(
                required=["jsonrpc", "method"],
                properties={
                    "jsonrpc": Fields.enum("2.0"),
                    "method": Fields.string,
                    "params": Fields.type("array", "object"),
                    "id": Fields.type(
                        "string",
                        "number",
                        "null",
                        note=[
                            "While allowed, null should be avoided: "
                            "http://www.jsonrpc.org/specification#id1",
                            "While allowed, a number with a fractional part should be avoided: "
                            "http://www.jsonrpc.org/specification#id2",
                        ],
                    ),
                },
            )
        },
    )

    RESPONSE: dict = Fields.oneof(
        Fields.ref("/definitions/response"),
        Fields.array(items=Fields.ref("/definitions/response")),
        **Fields.schema,
        definitions={
            "response": Fields.type(
                "array",
                "object",
                required=["jsonrpc"],
                properties={
                    "jsonrpc": Fields.enum("2.0"),
                    "id": Fields.type("string", "number", "null"),
                    "result": Fields.any,
                    "error": Fields.type(
                        "array",
                        "object",
                        properties={
                            "code": Fields.number,
                            "message": Fields.string,
                        },
                    ),
                },
            )
        },
    )
