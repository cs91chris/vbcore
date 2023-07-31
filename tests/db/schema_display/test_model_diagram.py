from sqlalchemy import Column, ForeignKey, types
from sqlalchemy.orm import class_mapper, relationship

from vbcore.db.schema_display.model_diagram import create_uml_graph

from .utils import parse_graph


def plain_result(mapper, **kw):
    return parse_graph(create_uml_graph(mapper, **kw))


def mappers(*args):
    return [class_mapper(x) for x in args]


def test_simple_class(Base, capsys):
    class Foo(Base):
        __tablename__ = "foo"
        id = Column(types.Integer, primary_key=True)

    result = plain_result(mappers(Foo))
    assert list(result.keys()) == ["1"]
    assert list(result["1"]["nodes"].keys()) == ["Foo"]
    assert "+ id: Integer" in result["1"]["nodes"]["Foo"]
    out, err = capsys.readouterr()
    assert out == ""
    assert err == ""


def test_relation(Base):
    class Foo(Base):
        __tablename__ = "foo"
        id = Column(types.Integer, primary_key=True)

    class Bar(Base):
        __tablename__ = "bar"
        id = Column(types.Integer, primary_key=True)
        foo_id = Column(types.Integer, ForeignKey(Foo.id))

    Foo.bars = relationship(Bar)
    graph = create_uml_graph(mappers(Foo, Bar))
    assert sorted(graph.obj_dict["nodes"].keys()) == ['"Bar"', '"Foo"']
    assert "+ id: Integer" in graph.obj_dict["nodes"]['"Foo"'][0]["attributes"]["label"]
    assert "- foo_id: Integer" in graph.obj_dict["nodes"]['"Bar"'][0]["attributes"]["label"]
    assert "edges" in graph.obj_dict
    assert ('"Foo"', '"Bar"') in graph.obj_dict["edges"]
    assert graph.obj_dict["edges"][('"Foo"', '"Bar"')][0]["attributes"]["headlabel"] == "bars *"


def test_backref(Base):
    class Foo(Base):
        __tablename__ = "foo"
        id = Column(types.Integer, primary_key=True)

    class Bar(Base):
        __tablename__ = "bar"
        id = Column(types.Integer, primary_key=True)
        foo_id = Column(types.Integer, ForeignKey(Foo.id))

    Foo.bars = relationship(Bar, backref="foo")
    graph = create_uml_graph(mappers(Foo, Bar))
    assert sorted(graph.obj_dict["nodes"].keys()) == ['"Bar"', '"Foo"']
    assert "+ id: Integer" in graph.obj_dict["nodes"]['"Foo"'][0]["attributes"]["label"]
    assert "- foo_id: Integer" in graph.obj_dict["nodes"]['"Bar"'][0]["attributes"]["label"]
    assert "edges" in graph.obj_dict
    assert ('"Foo"', '"Bar"') in graph.obj_dict["edges"]
    assert ('"Bar"', '"Foo"') in graph.obj_dict["edges"]
    assert graph.obj_dict["edges"][('"Foo"', '"Bar"')][0]["attributes"]["headlabel"] == "bars *"
    assert graph.obj_dict["edges"][('"Bar"', '"Foo"')][0]["attributes"]["headlabel"] == "foo 0..1"
