import datetime

from sqlalchemy.sql import table, column, select, update, insert

from flask import current_app as app

from genesis_blockchain_api_client.blockchain.block import (
    Block, get_block_id_from_dict, get_block_data_from_dict
)
from genesis_blockchain_api_client.blockchain.block_set import BlockSet
from genesis_blockchain_api_client.blockchain.tx import Tx
from genesis_blockchain_api_client.blockchain.tx_set import TxSet

from .....db import db
from .....logging import get_logger
from .....models.db_engine.session import SessionManager
from .....utils import is_number, ts_to_fmt_time
from .....blockchain import (
    get_block, get_block_data,
    get_detailed_block, get_detailed_block_data,
)

from .param import ParamModel
#from ..block import BlockModel

def get_tx_params_model(bind_key=None):
    from .param import ParamModel
    if bind_key:
        ParamModel.__bind_key__ = bind_key
    return ParamModel

logger = get_logger(app) 
sm = SessionManager(app=app)

class Error(Exception):
    pass

class TxModel(db.Model):

    __tablename__ = 'transactions'
    #__bind_key__ = 'genesis_aux'
    #__table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    block_id = db.Column(db.Integer, db.ForeignKey('blocks.id'))

    # main
    hash = db.Column(db.String)
    contract_name = db.Column(db.String)
    key_id = db.Column(db.Integer)
    ukey_id = db.Column(db.Integer)
    time_ts = db.Column(db.Integer)
    time_dt = db.Column(db.DateTime)
    type = db.Column(db.Integer)
    params = db.relationship('ParamModel', uselist=True,
                             backref=db.backref('transactions'))

    @classmethod
    def prepare_from_dict(cls, data, **kwargs):
        if 'key_id' in data:
            if data['key_id']:
                data['ukey_id'] = int(data['key_id']) & 0xffffffffffffffff
            else:
                data['ukey_id'] = 0
        if 'time' in data:
            time_ts = int(data.pop('time'))
            time_dt = datetime.datetime.fromtimestamp(time_ts)
        else:
            time_ts = 0
            time_dt = datetime.datetime.fromtimestamp(time_ts)
        data['time_ts'] = time_ts
        data['time_dt'] = time_dt

        params_dicts = []
        if 'params' in data:
            params = data.pop('params')
            for name, value in params.items():
                d = {'name': name, 'value': value}
                params_dicts.append(d)
        return data, params_dicts

    @classmethod
    def update_from_dict(cls, data, **kwargs):
        print("TxModel.update_from_dict cls.__bind__key__: %s" % cls.__bind_key__)
        ParamModel = get_tx_params_model(cls.__bind_key__)
        data, params_dicts = cls.prepare_from_dict(data)
        logger.debug("data: %s" % data)
        logger.debug("params_dicts: %s" % params_dicts)

        tx = cls(**data)
        db.session.add(tx)
        for param in params_dicts:
            name = tuple(param.keys())[0]
            value = param[name]
            p = ParamModel(name=name, value=value)
            tx.params.append(p)
        if kwargs.get('db_session_commit_enabled', True):
            db.session.commit()
        return tx

    @classmethod
    def update_from_list_of_dicts(cls, data, **kwargs):
        l = []
        for item in data:
            l.append(cls.update_from_dict(item, db_session_commit_enabled=False))
        db.session.commit()
        return l

    @classmethod
    def update_from_tx(cls, tx, **kwargs):
        data = tx.to_dict(style='snake')
        return cls.update_from_dict(data)

    @classmethod
    def update_from_tx_set(cls, tx_set, **kwargs):
        txs = tx_set.to_list(style='snake')
        return cls.update_from_list_of_dicts(txs)


