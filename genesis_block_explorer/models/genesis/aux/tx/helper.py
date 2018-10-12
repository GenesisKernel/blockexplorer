from flask import current_app as app

from .....db import db
from .....logging import get_logger
from ..generic.helper import GenericHelperBaseModel, GenericHelperManager

logger = get_logger(app) 

class TxHelperBaseModel(GenericHelperBaseModel):
    __abstract__ = True
    hash = db.Column(db.String, comment="Hash")

    @classmethod
    def get_drop_fields(cls):
        return ['id']

    @classmethod
    def update_from_main_model_instance(cls, mm_instance, **kwargs):
        seq_num, session, main_model_session, drop_fields, src_col_names, use_column_comment = cls.prep_from_main_model_instance(mm_instance, **kwargs)
        for col_name, col_comment in src_col_names.items():
            d = {
                'name': col_name,
                'label': col_comment if col_comment else col_name,
                'seq_num': seq_num,
                'hash': mm_instance.hash,
                'value': getattr(mm_instance, col_name)
            }
            record = session.merge(cls(**d))
        if kwargs.get('db_session_commit_enabled', True):
            session.commit() 

class TxHelperModel(TxHelperBaseModel):
    __tablename__ = 'aux_transaction_helper'

class TxHelperManager(GenericHelperManager):
    def __init__(self, **kwargs):
        super(TxHelperManager, self).__init__(model=TxHelperModel, **kwargs)

