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
from .....utils import is_number, ts_to_fmt_time
from .....blockchain import (
    get_block, get_block_data,
    get_detailed_block, get_detailed_block_data,
)

from .param import ParamModel

def get_tx_params_model(bind_key=None):
    from .param import ParamModel
    if bind_key:
        ParamModel.__bind_key__ = bind_key
    return ParamModel

logger = get_logger(app) 

class Error(Exception):
    pass

class TxModel(db.Model):

    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True)
    block_id = db.Column(db.Integer, db.ForeignKey('blocks.id'))

    # main
    hash = db.Column(db.String)
    contract_name = db.Column(db.String)
    key_id = db.Column(db.BigInteger)
    ukey_id = db.Column(db.String)
    time_ts = db.Column(db.Integer)
    time_dt = db.Column(db.DateTime)
    type = db.Column(db.Integer)
    params = db.relationship('ParamModel', uselist=True,
                             backref=db.backref('transactions'))

    @classmethod
    def prepare_from_dict(cls, data, **kwargs):
        if 'key_id' in data:
            if data['key_id']:
                data['ukey_id'] = str(int(data['key_id']) & 0xffffffffffffffff)
            else:
                data['ukey_id'] = '0'
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
        logger.debug("data: %s" % data)
        logger.debug("params_dicts: %s" % params_dicts)

        tx = cls(**data)
        session.add(tx)
        for param in params_dicts:
            name = tuple(param.keys())[0]
            value = param[name]
            p = ParamModel(name=name, value=value)
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


