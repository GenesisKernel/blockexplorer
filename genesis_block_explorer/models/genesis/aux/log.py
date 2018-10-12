import enum
import os

from sqlalchemy import Enum, func

from flask import current_app as app

from ....db import db
from ....logging import get_logger

logger = get_logger(app) 

class Error(Exception):
    pass

class LogModel(db.Model):

    __tablename__ = 'logs'

    id = db.Column(db.Integer, primary_key=True)
    context = db.Column(db.String, default='default_context')
    caller = db.Column(db.String, default='default_caller')
    stage = db.Column(db.String)
    process_id = db.Column(db.Integer, default=os.getpid())
    created_at = db.Column(db.DateTime, default=func.now())

    @classmethod
    def add(cls, **kwargs):
        context = kwargs.get('context', 'default_context')
        caller = kwargs.get('caller', 'default_caller')
        stage = kwargs.get('stage')
        session = kwargs.get('session')
        e = cls(context=context, caller=caller, stage=stage)
        session.add(e)
        session.commit()

    @classmethod
    def clear(cls, **kwargs):
        context = kwargs.get('context', 'default_context')
        session = kwargs.get('session')
        session.query(LogModel).delete()
        session.commit()

