import sqlalchemy as sa

from vbcore.db.sqla import SQLAConnector, BaseModel, as_declarative
from vbcore.db.support import SQLASupport
from vbcore.db.views import DDLCreateView


@as_declarative()
class Model(BaseModel):
    pass


class SampleModel(Model):
    __tablename__ = "sample_view"

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String)


if __name__ == "__main__":
    connector = SQLAConnector("sqlite:///", echo=True)
    SQLASupport.register_custom_handlers(connector.engine)

    DDLCreateView(
        name="sample_view",
        metadata=connector.metadata,
        select=sa.select(sa.literal_column("1 AS id, 'name' as name")),
    )

    connector.create_all()
    with connector.connection() as session:
        query = sa.select(SampleModel.id, SampleModel.name)
        result = session.execute(query).all()
        print(result)
