from flask import current_app as app

from ......db import db
from ......logging import get_logger
from ..helper import (
    GenericHelperBaseModel, BlockHelperBaseModel, GenericHelperManager
)

logger = get_logger(app) 

class HeaderHelperBaseModel(BlockHelperBaseModel):
    __abstract__ = True

    @classmethod
    def get_drop_fields(cls):
        return ['id', 'hash']

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

class HeaderHelperModel(HeaderHelperBaseModel):
    __tablename__ = 'aux_header_helper'

class HeaderHelperManager(GenericHelperManager):
    def __init__(self, **kwargs):
        super(HeaderHelperManager, self).__init__(model=HeaderHelperModel, **kwargs)

