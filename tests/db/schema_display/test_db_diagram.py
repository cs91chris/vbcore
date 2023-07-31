import pydot
import pytest
from sqlalchemy import Column, ForeignKey, Table, types

from vbcore.db.schema_display.db_diagram import create_schema_graph

from .utils import parse_graph


def plain_result(**kw):
    if "metadata" in kw:
        kw["metadata"].create_all(kw["engine"])
    elif "tables" in kw:
        if len(kw["tables"]):
            kw["tables"][0].metadata.create_all(kw["engine"])
    return parse_graph(create_schema_graph(**kw))


def test_no_args(engine):
    with pytest.raises(ValueError) as e:
        create_schema_graph(engine=engine)
    assert e.value.args[0] == "You need to specify at least tables or metadata"


def test_empty_db(metadata, engine):
    graph = create_schema_graph(engine=engine, metadata=metadata)
    assert isinstance(graph, pydot.Graph)
    # noinspection PyUnresolvedReferences
    assert graph.create_plain() == b"graph 1 0 0\nstop\n"  # pylint: disable=no-member


def test_empty_table(metadata, engine):
    _ = Table("foo", metadata, Column("id", types.Integer, primary_key=True))
    result = plain_result(engine=engine, metadata=metadata)
    assert list(result.keys()) == ["1"]
    assert list(result["1"]["nodes"].keys()) == ["foo"]
    assert "+ id: INTEGER  (PK)" in result["1"]["nodes"]["foo"]


def test_empty_table_with_key_suffix(metadata, engine):
    _ = Table("foo", metadata, Column("id", types.Integer, primary_key=True))
    result = plain_result(
        engine=engine,
        metadata=metadata,
        show_column_keys=True,
    )
    assert list(result.keys()) == ["1"]
    assert list(result["1"]["nodes"].keys()) == ["foo"]
    assert "+ id: INTEGER  (PK)" in result["1"]["nodes"]["foo"]


def test_foreign_key(metadata, engine):
    foo_table = Table(
        "foo",
        metadata,
        Column("id", types.Integer, primary_key=True),
    )
    _ = Table(
        "bar",
        metadata,
        Column("foo_id", types.Integer, ForeignKey(foo_table.c.id)),
    )
    result = plain_result(engine=engine, metadata=metadata)
    assert list(result.keys()) == ["1"]
    assert sorted(result["1"]["nodes"].keys()) == ["bar", "foo"]
    assert "+ id: INTEGER" in result["1"]["nodes"]["foo"]
    assert "- foo_id: INTEGER (FK)" in result["1"]["nodes"]["bar"]
    assert "edges" in result["1"]
    assert ("bar", "foo") in result["1"]["edges"]


def test_foreign_key_with_key_suffix(metadata, engine):
    foo_table = Table(
        "foo",
        metadata,
        Column("id", types.Integer, primary_key=True),
    )
    _ = Table(
        "bar",
        metadata,
        Column("foo_id", types.Integer, ForeignKey(foo_table.c.id)),
    )
    result = plain_result(engine=engine, metadata=metadata, show_column_keys=True)
    assert list(result.keys()) == ["1"]
    assert sorted(result["1"]["nodes"].keys()) == ["bar", "foo"]
    assert "+ id: INTEGER  (PK)" in result["1"]["nodes"]["foo"]
    assert "- foo_id: INTEGER (FK)" in result["1"]["nodes"]["bar"]
    assert "edges" in result["1"]
    assert ("bar", "foo") in result["1"]["edges"]


def test_table_filtering(engine, metadata):
    foo_table = Table(
        "foo",
        metadata,
        Column("id", types.Integer, primary_key=True),
    )
    bar_table = Table(
        "bar",
        metadata,
        Column("foo_id", types.Integer, ForeignKey(foo_table.c.id)),
    )
    result = plain_result(engine=engine, tables=[bar_table])
    assert list(result.keys()) == ["1"]
    assert list(result["1"]["nodes"].keys()) == ["bar"]
    assert "- foo_id: INTEGER" in result["1"]["nodes"]["bar"]


def test_table_rendering_without_schema(metadata, engine):
    foo_table = Table(
        "foo",
        metadata,
        Column("id", types.Integer, primary_key=True),
    )
    _ = Table(
        "bar",
        metadata,
        Column("foo_id", types.Integer, ForeignKey(foo_table.c.id)),
    )

    try:
        graph = create_schema_graph(engine=engine, metadata=metadata)
        # noinspection PyUnresolvedReferences
        graph.create_png()  # pylint: disable=no-member
    except Exception as exc:
        raise AssertionError(
            f"An exception of type {exc.__class__.__name__} "
            f"was produced when attempting to render a png of the graph"
        ) from exc


def test_table_rendering_with_schema(metadata, engine):
    foo_table = Table(
        "foo", metadata, Column("id", types.Integer, primary_key=True), schema="sch_foo"
    )
    _ = Table(
        "bar",
        metadata,
        Column("foo_id", types.Integer, ForeignKey(foo_table.c.id)),
        schema="sch_bar",
    )

    try:
        graph = create_schema_graph(engine=engine, metadata=metadata, show_schema_name=True)
        # noinspection PyUnresolvedReferences
        graph.create_png()  # pylint: disable=no-member
    except Exception as exc:
        raise AssertionError(
            f"An exception of type {exc.__class__.__name__} "
            f"was produced when attempting to render a png of the graph"
        ) from exc


def test_table_rendering_with_schema_and_formatting(metadata, engine):
    foo_table = Table(
        "foo", metadata, Column("id", types.Integer, primary_key=True), schema="sch_foo"
    )
    _ = Table(
        "bar",
        metadata,
        Column("foo_id", types.Integer, ForeignKey(foo_table.c.id)),
        schema="sch_bar",
    )

    try:
        graph = create_schema_graph(
            engine=engine,
            metadata=metadata,
            show_schema_name=True,
            format_schema_name={"fontsize": 8.0, "color": "#888888"},
            format_table_name={"bold": True, "fontsize": 10.0},
        )
        # noinspection PyUnresolvedReferences
        graph.create_png()  # pylint: disable=no-member
    except Exception as exc:
        raise AssertionError(
            f"An exception of type {exc.__class__.__name__} "
            f"was produced when attempting to render a png of the graph"
        ) from exc
