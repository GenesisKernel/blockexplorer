from flask import current_app as app

from sqlalchemy import exc, inspect

from ....logging import get_logger
from .config import get_num_of_backends
from .engine import get_aux_db_engines
from .session import AuxSessionManager as SessionManager

from .block import BlockModel
from .block.header import HeaderModel
from .tx import TxModel
from .tx.param import ParamModel
from .member import MemberModel

logger = get_logger(app)

def db_is_empty(engine):
    table_names = inspect(engine).get_table_names()
    is_empty = table_names == []
    logger.debug("engine: %s, db is empty: %s" % (engine, is_empty))
    return is_empty

def table_exists(engine, name):
    exists = engine.dialect.has_table(engine, name)
    logger.debug("engine: %s, table '%s' exists: %s" % (engine, name, exists))
    return exists

def create_models_tables_for_engine(engine, models=[],
                                    recreate_if_exists=False):
    for model in models:
        create = False
        exists = table_exists(engine, model.__tablename__)
        if recreate_if_exists:
            try:
                model.__table__.drop(engine)
                create = True
            except (exc.OperationalError, exc.ProgrammingError) as e:
                logger.info("Can'n drop table '%s' for model '%s', error: %s" % (model.__tablename__, model, e))

        if not exists or create:
            try:
                model.__table__.create(engine)
            except (exc.OperationalError, exc.ProgrammingError) as e:
                logger.info("Can'n create table '%s' for model '%s', error: %s" % (model, model, e))

class TableManager:
    def __init__(self, **kwargs):
        self.app = kwargs.get('app', app)
        self.num_of_backends = kwargs.get('num_of_backends',
                                          get_num_of_backends(self.app))
        self.models = kwargs.get('models', [HeaderModel, BlockModel,
                                            TxModel, ParamModel,
                                            MemberModel])
        self.sm = kwargs.get('session_manager', SessionManager(app=self.app))
        self.recreate_if_exists = kwargs.get('recreate_if_exists', False)

    def create_tables(self):
        for seq_num in range(1, self.num_of_backends + 1):
            create_models_tables_for_engine(self.sm.get_engine(seq_num),
                    self.models, recreate_if_exists=self.recreate_if_exists)
        

