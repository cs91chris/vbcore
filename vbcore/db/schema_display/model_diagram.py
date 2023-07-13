"""
Set of functions to generate the diagram related to the ORM models
"""
import types
from typing import Any, cast, List, Tuple

import pydot
from sqlalchemy.orm import Mapper, Relationship
from sqlalchemy.orm.properties import RelationshipProperty


def _mk_label(
    mapper: Mapper,
    show_operations: bool,
    show_attributes: bool,
    show_datatypes: bool,
    show_inherited: bool,
    bordersize: float,
) -> str:
    # pylint: disable=too-many-arguments
    """Generate the rendering of a given orm model.
    Args:
        mapper (sqlalchemy.orm.Mapper): mapper for the SqlAlchemy orm class.
        show_operations (bool): whether to show functions defined in the orm.
        show_attributes (bool): whether to show the attributes of the class.
        show_datatypes (bool): Whether to display the type of the columns in the model.
        show_inherited (bool): whether to show inherited columns.
        bordersize (float): thickness of the borderlines in the diagram
    Returns:
        str: html string to render the orm model
    """
    html = (
        f'<<TABLE CELLSPACING="0" CELLPADDING="1" BORDER="0" CELLBORDER="{bordersize}" '
    )
    html += f'ALIGN="LEFT"><TR><TD><FONT POINT-SIZE="10">{mapper.class_.__name__}</FONT></TD></TR>'

    def format_col(col):
        sep = "-" if col.nullable else "+"
        colstr = f"{sep} {col.name}"
        if show_datatypes:
            colstr += f": {col.type.__class__.__name__}"
        return colstr

    if show_attributes:
        if not show_inherited:
            cols = [c for c in mapper.columns if c.table == mapper.tables[0]]
        else:
            cols = list(mapper.columns)
        # pylint: disable=consider-using-f-string
        html += '<TR><TD ALIGN="LEFT">%s</TD></TR>' % '<BR ALIGN="LEFT"/>'.join(
            format_col(col) for col in cols
        )
    else:
        _ = [
            format_col(col)
            for col in sorted(mapper.columns, key=lambda col: not col.primary_key)
        ]
    if show_operations:

        def zip_func(_func):
            return zip(
                (
                    _func.func_defaults
                    and len(_func.func_code.co_varnames)
                    - 1
                    - (len(_func.func_defaults) or 0)
                    or _func.func_code.co_argcount - 1
                )
                * [_mk_label]
                + list(_func.func_defaults or []),
                _func.func_code.co_varnames[1:],
                strict=False,
            )

        # pylint: disable=consider-using-f-string
        html += '<TR><TD ALIGN="LEFT">%s</TD></TR>' % '<BR ALIGN="LEFT"/>'.join(
            "%s(%s)"
            % (
                name,
                ", ".join(
                    default is _mk_label and f"{arg}" or f"{arg}={repr(default)}"
                    for default, arg in zip_func(func)
                ),
            )
            for name, func in cast(Tuple[str, Any], mapper.class_.__dict__.items())
            if isinstance(func, types.FunctionType)
            and func.__module__ == mapper.class_.__module__
        )
    html += "</TABLE>>"
    return html


def escape(name: str) -> str:
    """Set the name of the object between quotations to avoid reading errors
    Args:
        name (str): name of the object
    Returns:
        str: name of the object between quotations to avoid reading errors
    """
    return f'"{name}"'


def create_uml_graph(  # noqa: C901
    mappers: List[Mapper],
    show_operations: bool = True,
    show_attributes: bool = True,
    show_inherited: bool = True,
    show_multiplicity_one: bool = True,
    show_datatypes: bool = True,
    linewidth: float = 1.0,
    font: str = "monospace",
) -> pydot.Dot:
    # pylint: disable=too-many-locals,too-many-arguments
    """Create rendering of the orm models associated with the database
    Args:
        mappers (List[sqlalchemy.orm.Mapper]): SqlAlchemy list of mappers of the orm classes.
        show_operations (bool, optional): whether to show functions defined in the orm. \
            Defaults to True.
        show_attributes (bool, optional): whether to show the attributes of the class. \
            Defaults to True.
        show_inherited (bool, optional): whether to show inherited columns. Defaults to True.
        show_multiplicity_one (bool, optional): whether to show the multiplicity as a float or \
            integer. Defaults to False.
        show_datatypes (bool, optional): Whether to display the type of the columns in the model. \
            Defaults to True.
        linewidth (float, optional): thickness of the lines in the diagram. Defaults to 1.0.
        font (str, optional): type of fond to be used for the diagram. \
            Defaults to "Bitstream-Vera Sans".
    Returns:
        pydot.Dot: pydot object with the diagram for the orm models.
    """
    graph = pydot.Dot(
        prog="neato",
        mode="major",
        overlap="0",
        dim="3",
        pack="True",
        ratio=".75",
    )
    relations = set()
    for mapper in mappers:
        graph.add_node(
            pydot.Node(
                escape(mapper.class_.__name__),
                shape="plaintext",
                label=_mk_label(
                    mapper,
                    show_operations,
                    show_attributes,
                    show_datatypes,
                    show_inherited,
                    linewidth,
                ),
                fontname=font,
                fontsize="8.0",
            )
        )
        if mapper.inherits:
            graph.add_edge(
                pydot.Edge(
                    escape(mapper.inherits.class_.__name__),
                    escape(mapper.class_.__name__),
                    arrowhead="none",
                    arrowtail="empty",
                    style=f"setlinewidth({linewidth})",
                    arrowsize=str(linewidth),
                ),
            )
        for loader in mapper.iterate_properties:
            if isinstance(loader, RelationshipProperty) and loader.mapper in mappers:
                if hasattr(loader, "reverse_property"):
                    relations.add(frozenset([loader, loader.reverse_property]))
                else:
                    relations.add(frozenset([loader]))

    def multiplicity_indicator(prop: Relationship) -> str:
        """
        Indicate the multiplicity of a given relationship
        Args:
            prop (sqlalchemy.orm.Relationship): relationship associated with this model
        Returns:
            str: string indicating the multiplicity of the relationship
        """
        if prop.uselist:
            return " *"

        cols = prop.local_side if hasattr(prop, "local_side") else prop.local_columns
        if any(col.nullable for col in cols):
            return " 0..1"

        return " 1" if show_multiplicity_one else ""

    for relation in relations:
        args = {}

        if len(relation) == 2:
            src, dest = relation
            from_name = escape(src.parent.class_.__name__)
            to_name = escape(dest.parent.class_.__name__)

            args["headlabel"] = src.key + multiplicity_indicator(src)
            args["taillabel"] = dest.key + multiplicity_indicator(dest)
            args["arrowtail"] = "none"
            args["arrowhead"] = "none"
            args["constraint"] = False
        else:
            (_prop,) = relation
            from_name = escape(_prop.parent.class_.__name__)
            to_name = escape(_prop.mapper.class_.__name__)
            args["headlabel"] = f"{_prop.key}{multiplicity_indicator(_prop)}"
            args["arrowtail"] = "none"
            args["arrowhead"] = "vee"

        graph.add_edge(
            pydot.Edge(
                from_name,
                to_name,
                fontname=font,
                fontsize="7.0",
                style=f"setlinewidth({linewidth})",
                arrowsize=str(linewidth),
                **args,
            ),
        )

    return graph
