from flask import current_app as app

from sqlalchemy import exc

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

def create_models_tables_for_engine(engine, models=[],
                                    recreate_if_exists=False):
    for model in models:
        if recreate_if_exists:
            try:
                model.__table__.drop(engine)
            except exc.OperationalError as e:
                logger.info("Can'n drop table '%s' for model '%s', error: %s" % (model.__tablename__, model, e))

        try:
            model.__table__.create(engine)
        except exc.OperationalError as e:
            logger.info("Can'n create table '%s' for model '%s', error: %s" % (model, model, e))

class TableManager:
    def __init__(self, **kwargs):
        self.app = kwargs.get('app', app)
        self.num_of_backends = kwargs.get('num_of_backends',
                                          get_num_of_backends(self.app))
        self.models = kwargs.get('models', [BlockModel, HeaderModel, TxModel,
                                            ParamModel, MemberModel])
        self.sm = kwargs.get('session_manager', SessionManager(app=self.app))
        self.recreate_if_exists = kwargs.get('recreate_if_exists', False)

    def create_tables(self):
        for seq_num in range(1, self.num_of_backends + 1):
            create_models_tables_for_engine(self.sm.get_engine(seq_num),
                    self.models, recreate_if_exists=self.recreate_if_exists)
        

