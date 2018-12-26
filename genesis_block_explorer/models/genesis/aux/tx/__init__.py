from sqlalchemy import exc
from sqlalchemy.ext.hybrid import hybrid_method

from flask import current_app as app

from .....db import db
from .....logging import get_logger
from ..utils import update_dict_with_key_id, update_dict_with_time
from ..generic.prev_next_item import PrevNextItemMixin
from .param import ParamModel

def get_tx_params_model(bind_key=None):
    from .param import ParamModel
    if bind_key:
        ParamModel.__bind_key__ = bind_key
    return ParamModel

logger = get_logger(app) 

class Error(Exception):
    pass

class TxPrevNextItemMixin(PrevNextItemMixin):
    @hybrid_method
    def get_prev_next_info(self, **kwargs):
        session = kwargs.get('session', db.session)
        has_prev = self.has_prev(session=session)
        if has_prev:
            prev_tx_id = self.prev(session=session).id
            prev_tx_hash = self.prev(session=session).hash
        else:
            prev_tx_id = 0
            prev_tx_hash = ''
        has_next = self.has_next(session=session)
        if has_next:
            next_tx_id = self.next(session=session).id
            next_tx_hash = self.next(session=session).hash
        else:
            next_tx_id = 0
            next_tx_hash = ''
        info = {
            'has_prev': has_prev,
            'prev_tx_id': prev_tx_id, 
            'prev_tx_hash': prev_tx_hash, 
            'has_next': has_next,
            'next_tx_id': next_tx_id, 
            'next_tx_hash': next_tx_hash, 
        }
        return info

class TxModel(db.Model, TxPrevNextItemMixin):

    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True, comment="TX Record ID")
    time_dt = db.Column(db.String, comment="Time")
    hash = db.Column(db.String(512), index=True, comment="Hash")
    contract_name = db.Column(db.String, comment="Contract Name")
    address = db.Column(db.String, comment="Address")
    type = db.Column(db.Integer, comment="Type")
    block_id = db.Column(db.Integer, db.ForeignKey('blocks.id',
                                                   ondelete='CASCADE'),
                         comment="Block ID")

    # main
    key_id = db.Column(db.String, comment="Key ID")
    time_ts = db.Column(db.Integer, comment="Time (Stamp)")
    time_dtu = db.Column(db.String, comment="Time (UTC)")
    params = db.relationship('ParamModel', uselist=True,
                             cascade="all, delete-orphan",
                             backref=db.backref('transactions',
                                                cascade='delete'))

    @classmethod
    def prepare_from_dict(cls, data, **kwargs):
        data = update_dict_with_key_id(data)
        data = update_dict_with_time(data)
        params_dicts = []
        if 'params' in data:
            params = data.pop('params')
            if params:
                for name, value in params.items():
                    d = {'name': name, 'value': value}
                    params_dicts.append(d)
        return data, params_dicts

    @classmethod
    def update_from_dict(cls, data, **kwargs):
        session = kwargs.get('session', db.session)
        ParamModel = get_tx_params_model()
        data, params_dicts = cls.prepare_from_dict(data)
        #logger.debug("data: %s" % data)
        #logger.debug("params_dicts: %s" % params_dicts)

        tx = cls(**data)
        session.add(tx)
        for param in params_dicts:
            p = ParamModel(name=param['name'], value=str(param['value']))
            tx.params.append(p)
        if kwargs.get('db_session_commit_enabled', True):
            session.commit()
        return tx

    @classmethod
    def update_from_list_of_dicts(cls, data, **kwargs):
        session = kwargs.get('session', db.session)
        l = []
        for item in data:
            l.append(cls.update_from_dict(item, session=session,
                                          db_session_commit_enabled=False))
        
        if kwargs.get('db_session_commit_enabled', True):
            session.commit()
        return l

    @classmethod
    def update_from_tx(cls, tx, **kwargs):
        session = kwargs.get('session', db.session)
        data = tx.to_dict(style='snake')
        return cls.update_from_dict(data, session=session,
        db_session_commit_enabled=kwargs.get('db_session_commit_enabled', True))

    @classmethod
    def update_from_tx_set(cls, tx_set, **kwargs):
        session = kwargs.get('session', db.session)
        txs = tx_set.to_list(style='snake')
        return cls.update_from_list_of_dicts(txs, session=session,
        db_session_commit_enabled=kwargs.get('db_session_commit_enabled', True))

    @hybrid_method
    def delete(self, **kwargs):
        session = kwargs.get('session', db.session)
        if self.params:
            self.params.clear()
        session.delete(self)
        if kwargs.get('db_session_commit_enabled', True):
            try:
                session.commit()
            except exc.SQLAlchemyError:
                session.rollback()
            
    @classmethod
    def clear(cls, **kwargs):
        session = kwargs.get('session', db.session)
        [i.delete(session=session, db_session_commit_enabled=False) for i in session.query(cls).all()]
        if kwargs.get('db_session_commit_enabled', True):
            try:
                session.commit()
            except exc.SQLAlchemyError:
                session.rollback()
