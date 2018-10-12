from decimal import Decimal 

from flask import current_app as app

from .....db import db
from .....logging import get_logger
from ..generic.helper import (
    GenericHelperBaseModel, GenericHelperManager
)

logger = get_logger(app) 

class MemberHelperBaseModel(GenericHelperBaseModel):
    __abstract__ = True
    ecosystem_id = db.Column(db.Integer, comment="Ecosystem ID")

    @classmethod
    def get_drop_fields(cls):
        return ['id']

    @classmethod
    def update_from_main_model_instance(cls, mm_instance, **kwargs):
        seq_num, session, main_model_session, drop_fields, src_col_names, use_column_comment = cls.prep_from_main_model_instance(mm_instance, **kwargs)
        ecosystem_id = kwargs.get('ecosystem_id')
        for col_name, col_comment in src_col_names.items():
            d = {
                'name': col_name,
                'label': col_comment if col_comment else col_name,
                'seq_num': seq_num,
                'ecosystem_id': ecosystem_id,
            }
            value = getattr(mm_instance, col_name)
            if type(value) == Decimal:
                value = str(value)
            d['value'] = value
            record = session.merge(cls(**d))
        if kwargs.get('db_session_commit_enabled', True):
            session.commit() 

class MemberHelperModel(MemberHelperBaseModel):
    __tablename__ = 'aux_member_helper'

class MemberHelperManager(GenericHelperManager):
    def __init__(self, **kwargs):
        super(MemberHelperManager, self).__init__(model=MemberHelperModel, **kwargs)

