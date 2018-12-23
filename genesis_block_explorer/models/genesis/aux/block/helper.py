from flask import current_app as app

from .....db import db
from .....logging import get_logger
from ..generic.helper import GenericHelperBaseModel, GenericHelperManager

logger = get_logger(app) 

class BlockHelperBaseModel(GenericHelperBaseModel):
    __abstract__ = True
    block_id = db.Column(db.Integer, comment="Block ID")

    @classmethod
    def get_drop_fields(cls):
        return ['header_id', 'header', 'transactions', 'time_ts', 'time_dt', 'time_dtu', 'key_id', 'wallet', 'node_position', 'ecosystem_id']

    @classmethod
    def update_from_main_model_instance(cls, mm_instance, **kwargs):
        seq_num, session, main_model_session, drop_fields, src_col_names, use_column_comment = cls.prep_from_main_model_instance(mm_instance, **kwargs)
        for col_name, col_comment in src_col_names.items():
            d = {
                'name': col_name,
                'label': col_comment if col_comment else col_name,
                'seq_num': seq_num,
                'block_id': mm_instance.id,
                'value': getattr(mm_instance, col_name)
            }
            record = session.merge(cls(**d))
        if kwargs.get('db_session_commit_enabled', True):
            session.commit() 

class BlockHelperModel(BlockHelperBaseModel):
    __tablename__ = 'aux_block_helper'

class BlockHelperManager(GenericHelperManager):
    def __init__(self, **kwargs):
        super(BlockHelperManager, self).__init__(model=BlockHelperModel, **kwargs)

