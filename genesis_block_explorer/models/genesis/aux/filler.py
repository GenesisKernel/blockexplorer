from sqlalchemy import exc, func

from flask import current_app as app

from ....blockchain import (
    get_max_block_id,
    get_detailed_block,
    get_detailed_block_data,
    get_detailed_blocks,
    get_detailed_blocks_data,
)

from ....utils import is_number, is_string
from ....logging import get_logger
from ...db_engine.session import SessionManager
from .session import AuxSessionManager
from .block import BlockModel
from .tx import TxModel
from .tx.param import ParamModel

logger = get_logger(app) 

class Filler:
    def __init__(self, **kwargs):
        self.involved_models = kwargs.get('involved_models',
                                          (BlockModel, TxModel, ParamModel))
        self.seq_num = kwargs.get('seq_num', 1)
        self.app = kwargs.get('app', None)
        self.create_tables = kwargs.get('create_tables', True)
        self.recreate_tables_if_exist = kwargs.get('recreate_tables_if_exist',
                                                   False)
        self.bc_sm = SessionManager(app=self.app)
        self.aux_sm = AuxSessionManager(app=self.app)
        if self.create_tables:
            self.do_create_tables()

    def do_create_tables(self, **kwargs):
        recreate_tables_if_exist = kwargs.get('recreate_tables_if_exist', 
                                              self.recreate_tables_if_exist)
        engine = self.aux_sm.get_engine(self.seq_num)
        for model in self.involved_models:
            if recreate_tables_if_exist:
                try:
                    model.__table__.drop(engine)
                except exc.OperationalError as e:
                    logger.warning("Recreate if exists mode: can't drop table for model %s, error: %s" % (model, e))
            try:
                model.__table__.create(engine)
            except exc.OperationalError as e:
                logger.warning("Can'n create table for model %s, error: %s" % (model, e))

    def check_dbs(self):
        assert len(self.bc_sm.engines) == len(self.aux_sm.engines)
        assert len(self.bc_sm.sessions) == len(self.aux_sm.sessions)

    def fill_block(self, block_id, **kwargs):
        block_data = get_detailed_block_data(self.seq_num, block_id)
        return BlockModel.update_from_block(
            get_detailed_block(self.seq_num, block_id),
            session=self.aux_sm.get(self.seq_num)
        )

    def fill_all_blocks(self, **kwargs):
        max_block_id = get_max_block_id(self.seq_num)
        return BlockModel.update_from_block_set(
            get_detailed_blocks(self.seq_num, 1, max_block_id),
            session=self.aux_sm.get(self.seq_num)
        )
        
    def update(self):
        max_block_id = get_max_block_id(self.seq_num)
        session = self.aux_sm.get(self.seq_num)
        aux_max_block_id = session.query(func.max(BlockModel.id)).scalar()
        logger.info("max_block_id: %s aux_max_block_id: %s" % (max_block_id, aux_max_block_id))
        if not aux_max_block_id:
            return self.fill_all_blocks()
        else:
            return BlockModel.update_from_block_set(
                get_detailed_blocks(self.seq_num, aux_max_block_id + 1,
                                    max_block_id),
                session=self.aux_sm.get(self.seq_num)
            )


