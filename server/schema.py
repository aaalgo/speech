import enum
from types import SimpleNamespace
from marshmallow import Schema
from models import *

def make_schema (table):
    model_fields = []
    for c in table.columns:
        model_fields.append(c.name)

    class TableSchema (Schema):
        class Meta:
            fields = tuple(model_fields)
    return TableSchema(), TableSchema(many=True)

class AutoSchema:
    def __init__(self):
        self.schemas = {}

        for mapper in Base.registry.mappers:
            table = mapper.entity
            name = table.__tablename__
            one = SimpleNamespace()
            one.table = table
            one.schema, one.schema_many = make_schema(table.__table__)
            self.schemas[name] = one

    def get (self, session, table_name, pk, raw=False):
        assert table_name in self.schemas, f"Unknown table: {table_name}"
        schema = self.schemas[table_name]
        obj = session.get(schema.table, pk)
        if raw:
            return obj
        return schema.schema.dump(obj)

    def query (self, session, table_name, args, raw=False):
        assert table_name in self.schemas, f"Unknown table: {table_name}"
        schema = self.schemas[table_name]
        objs = session.query(schema.table)
        kargs = []
        order = []
        
        for k, v in args.items():
            if k == 'order_by':
                for cn in v.split(','):
                    if '__' in cn:
                        cn, desc = cn.split('__')
                        assert desc == 'desc'
                    else:
                        desc = None
                    c = schema.table.__table__.columns[cn]
                    if desc is None:
                        order.append(c)
                    else:
                        order.append(c.desc())
                continue
            if len(fs) != 2:
                continue
            k, op = fs
            c = schema.table.__table__.columns[k]
            try:
                value = c.type.python_type(v)
            except:
                continue
            if op == 'eq':
                kargs.append(c == value)
            elif op == 'lt':
                kargs.append(c < value)
            elif op == 'gt':
                kargs.append(c > value)
            elif op == 'in':
                kargs.append(c.in_(value))
            elif op == 'contains':
                kargs.append(c.contains(value))
            else:
                continue
        if len(kargs) > 0:
            objs = objs.filter(*kargs)
        if order:
            objs = objs.order_by(*order)
        objs = objs.all()
        if raw:
            return objs
        return schema.schema_many.dump(objs)