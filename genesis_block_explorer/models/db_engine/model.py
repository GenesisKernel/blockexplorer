from .automap import automapped_classes
from .database import Database, Table, db
from .engine import get_discovered_db_engines

from ..utils import (
    camelize_and_dedigitize_genesis_classname
)

from ...utils import import_attrs

def get_model_data_by_table(table, **kwargs):
    model_name = camelize_and_dedigitize_genesis_classname(None,
                                                           table.name, None)
    model = automapped_classes[table.database.bind_name][model_name]

    extend_mixin = kwargs.get('extend_with_mixin', None)
    extend_mixins = kwargs.get('extend_with_mixins', None)
    if extend_mixins:
        model = import_attrs(model, extend_mixins, multiple_src=True)
    elif extend_mixin:
        model = import_attrs(model, extend_mixin, multiple_src=False)

    return (model_name, model)

def get_model_data_by_table_id(table_id, **kwargs):
    table = Table.query.filter_by(id=table_id).one()
    model_name, model = get_model_data_by_table(table, **kwargs)
    columns = model.__table__.columns
    return (table, model, model_name)

def get_model_data_by_db_id_and_table_name(db_id, table_name, **kwargs):
    table = Table.query.filter_by(database_id=db_id).filter_by(name=table_name).one()
    model_name, model = get_model_data_by_table(table, **kwargs)
    return (table, model, model_name)

class ModelManager:
    def __init__(self, **kwargs):
        pass
        

