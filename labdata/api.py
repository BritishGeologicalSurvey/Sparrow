from flask import Flask, Blueprint
from flask_restful import Resource, Api, reqparse, inputs
from sqlalchemy.schema import Table
from sqlalchemy import MetaData

# eventually should use **Marshmallow** or similar
# for parsing incoming API requests

class APIv1(Api):
    """
    Version 1 API for Lab Data Interface

    Includes functionality for autogenerating routes
    from database tables and views.
    """
    def __init__(self, database):
        self.db = database
        self.blueprint = Blueprint('api', __name__)
        super().__init__(self.blueprint)
        self.route_descriptions = []
        self.create_description_model()

    def create_description_model(self):
        route_descriptions = self.route_descriptions
        class APIDescriptionModel(Resource):
            def get(self):
                return dict(
                    route='/ap1/v1',
                    description='Version 1 API for Lab Data Interface',
                    routes=route_descriptions
                )
        self.add_resource(APIDescriptionModel, '/', '/describe')


    def build_route(self, tablename, **kwargs):
        schema = kwargs.pop('schema', None)
        db = self.db
        table = db.reflect_table(tablename, schema=schema)

        schema_qualified_tablename = tablename
        if schema is not None:
            schema_qualified_tablename = schema+"."+schema_qualified_tablename
        description = f"Autogenerated route for table '{schema_qualified_tablename}'"

        def infer_primary_key():
            pk = table.primary_key
            if len(pk) == 1:
                return list(pk)[0]
            # Check PK column a few possible ways
            primary_key = kwargs.pop("primary_key", None)
            if primary_key is not None:
                return table.c[primary_key]
            for i in ('id', tablename+'_id'):
                pk = table.c.get(i, None)
                if pk is not None: return pk
            return list(table.c)[0]

        def infer_type(t):
            # Really hackish
            type = t.type.python_type
            if type == bool:
                type = inputs.boolean
            return type

        key = infer_primary_key()

        parser = reqparse.RequestParser()
        parser.add_argument('offset', type=int, help='Query offset', default=0)
        parser.add_argument('limit', type=int, help='Query limit', default=100)

        for name, column in table.c.items():
            try:
                type = infer_type(column)
                typename = type.__name__
                parser.add_argument(name, type=type,
                    help=f"Column '{name}' of type '{typename}'")
            except: pass

        class TableModel(Resource):
            def get(self):
                args = parser.parse_args()
                print(args)
                q = db.session.query(table)

                for k,col in table.c.items():
                    val = args.pop(k, None)
                    if val is not None:
                        q = q.filter(col==val)

                for k in ('offset','limit'):
                    val = args.pop(k, None)
                    if val is not None:
                        q = getattr(q,k)(val)

                return q.all()

        class RecordModel(Resource):
            def get(self, id):
                # Should fail if more than one record is returned
                return (db.session.query(table)
                    .filter(key==id)
                    .first())

        route = f"/{tablename}"
        tname = infer_type(key).__name__
        if tname != 'int':
            tname = 'string'
        get_route = f"{route}/<{tname}:id>"
        describe_route = f"{route}/describe"

        basicInfo = dict(
            route=route,
            table=table.name,
            schema=table.schema,
            description=description
        )
        self.route_descriptions.append(basicInfo)

        class DescriptionModel(Resource):
            def get(self):
                args = [dict(
                    name=a.name,
                    default=a.default,
                    type=a.type.__name__,
                    description=a.help
                ) for a in parser.args]

                return dict(
                    **basicInfo,
                    arguments=args,
                    record=dict(
                        route=get_route,
                        key=key.name,
                        type=tname
                    )
                )


        # Dynamically change class name,
        # this kind of metaprogrammy wizardry
        # may cause problems later
        TableModel.__name__ = tablename
        RecordModel.__name__ = tablename+'_record'
        DescriptionModel.__name__ = tablename+'_describe'

        self.add_resource(TableModel, route)
        self.add_resource(RecordModel, get_route)
        self.add_resource(DescriptionModel, describe_route)
