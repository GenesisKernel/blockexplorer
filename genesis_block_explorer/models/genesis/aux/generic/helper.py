from sqlalchemy import MetaData, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from flask import current_app as app

from .....db import db
from .....logging import get_logger

logger = get_logger(app) 
metadata = MetaData()
Base = declarative_base(metadata=metadata, name='Base')

class Error(Exception): pass
class NoSessionIsSetError(Error): pass
class NoMainModelSessionIsSetError(Error): pass

class GenericHelperBaseModel(Base):
    __abstract__ = True

    @classmethod
    def get_drop_fields(cls):
        return []

    id = db.Column(db.Integer, primary_key=True, comment="Record ID")
    seq_num = db.Column(db.Integer, comment="Backend Sequence Number")
    name = db.Column(db.String, comment="name")
    label = db.Column(db.String, comment="Name")
    value = db.Column(db.Text, comment="Value")

    @classmethod
    def prep_from_main_model_instance(cls, mm_instance, **kwargs):
        seq_num = kwargs.get('seq_num', 0)
        session = kwargs.get('session')
        drop_fields = kwargs.get('drop_fields', cls.get_drop_fields())
        if not session:
            raise NoSessionIsSetError()
        main_model_session = kwargs.get('main_model_session')
        if not main_model_session:
            raise NoMainModelSessionIsSetError()
        src_col_names = dict([(c.name, c.comment) for c in mm_instance.__table__.columns if c.name not in drop_fields])
        use_column_comment = kwargs.get('use_column_comment', True)
        return seq_num, session, main_model_session, drop_fields, src_col_names, use_column_comment

class GenericHelperManager:
    def __init__(self, **kwargs):
        self.app = kwargs.get('app', app)
        self.base = kwargs.get('base', Base)
        self.metadata = kwargs.get('metadata', metadata)
        self.engine_options = kwargs.get('engine_options', {'connect_args': {'check_same_thread': False}, 'poolclass': StaticPool, 'echo': kwargs.get('engine_echo', False)})
        self.engine = kwargs.get('engine', create_engine('sqlite://', **self.engine_options))
        self.model = kwargs.get('model')
        self.metadata.create_all(self.engine, tables=[self.model.__table__])
        self.session = sessionmaker(bind=self.engine)()

    def __del__(self):
        self.metadata.drop_all(self.engine, tables=[self.model.__table__])
