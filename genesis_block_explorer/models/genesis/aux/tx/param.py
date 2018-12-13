from flask import current_app as app

from .....db import db
from .....logging import get_logger

logger = get_logger(app) 

class ParamModel(db.Model):

    __tablename__ = 'tx_params'

    id = db.Column(db.Integer, primary_key=True, comment="Parameter record ID")
    tx_id = db.Column(db.Integer, db.ForeignKey('transactions.id',
                                                ondelete='CASCADE'),
                      comment="TX ID")

    name = db.Column(db.String, comment="Name")
    value = db.Column(db.Text, comment="Value")

    @classmethod
    def prepare_from_dict(cls, data, **kwargs):
        if kwargs.get('from_struct_style', 'simple_dict'):
            if kwargs.get('to_struct_style', 'simple_dict'):
                return data
            else:
                return {'name': tuple(a.keys())[0],
                        'value': tuple(a.keys())[0]}
        else:
            if kwargs.get('to_struct_style', 'simple_dict'):
                return {tuple(a.keys())[0]: tuple(a.keys())[0]}
            else:
                return data

    @classmethod
    def update_from_dict(cls, data, **kwargs):
        session = kwargs.get('session', db.session)
        param_data = cls.prepare_from_dict(data,
               from_struct_style=kwargs.get('from_struct_style', 'simple_dict'),
               to_struct_style='sqlalchemy')
        param = cls(**param_data)
        session.add(param)
        if kwargs.get('db_session_commit_enabled', True):
            session.commit()
        return param

    @classmethod
    def update_from_param(cls, param, **kwargs):
        session = kwargs.get('session', db.session)
        data = param.to_dict(struct_style='sqlalchemy')
        return cls.update_from_dict(data, session=session,
            db_session_commit_enabled=kwargs.get('db_session_commit_enabled',
                                                 True))

    @classmethod
    def update_from_param_set(cls, param_set, **kwargs):
        session = kwargs.get('session', db.session)
        l = []
        for param in param_set:
            l.append(cls.update_from_param(param, session=session,
                                           db_session_commit_enabled=False))
        if kwargs.get('db_session_commit_enabled', True):
            session.commit()
        return l

