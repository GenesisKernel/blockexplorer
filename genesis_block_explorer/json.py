from flask.json import JSONEncoder

class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        from .models.db_engine.database import Database, Table, Column
        from decimal import Decimal
        try:
            if isinstance(obj, Decimal):
                return str(obj)
            if isinstance(obj, Database):
                return obj.as_dict()
            elif isinstance(obj, Table):
                return obj.as_dict()
            elif isinstance(obj, Column):
                return obj.as_dict()

            iterable = iter(obj)
        except TypeError:
            pass
        else:
            return list(iterable)
        return JSONEncoder.default(self, obj)

