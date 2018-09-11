import datetime

from sqlalchemy.sql import table, column, select, update, insert

from flask import current_app as app

from genesis_blockchain_api_client.blockchain.block import Block
from genesis_blockchain_api_client.blockchain.block_set import BlockSet

from ....db import db
from ....logging import get_logger
#from ....models.db_engine.engine import merge_two_dicts
from ....utils import is_number, ts_to_fmt_time
from ....blockchain import (
    get_block, get_block_data,
    get_detailed_block, get_detailed_block_data,
)
from .session import AuxSessionManager

def get_tx_and_tx_params_models(bind_key=None):
    from .tx import TxModel
    from .tx.param import ParamModel
    if bind_key:
        TxModel.__bind_key__ = bind_key
        ParamModel.__bind_key__ = bind_key
    return TxModel, ParamModel

logger = get_logger(app) 
get_tx_and_tx_params_models()

class Error(Exception):
    pass

class BlockModel(db.Model):

    __tablename__ = 'blocks'

    id = db.Column(db.Integer, primary_key=True)

    #header
    h_block_id = db.Column(db.Integer)
    h_time = db.Column(db.Integer)
    h_ecosystem_id = db.Column(db.Integer)
    h_key_id = db.Column(db.BigInteger)
    h_ukey_id = db.Column(db.String)
    h_node_position = db.Column(db.Integer)
    h_sign = db.Column(db.String)
    h_hash = db.Column(db.String)
    h_version = db.Column(db.Integer)

    # main
    hash = db.Column(db.String)
    ecosystem_id = db.Column(db.Integer)
    node_position = db.Column(db.Integer)
    key_id = db.Column(db.BigInteger)
    ukey_id = db.Column(db.String)
    time_ts = db.Column(db.Integer)
    time_dt = db.Column(db.DateTime)
    tx_count = db.Column(db.Integer)
    rollbacks_hash = db.Column(db.String)
    mrkl_root = db.Column(db.String)
    bin_data = db.Column(db.String)
    gen_block = db.Column(db.Boolean)
    sys_update = db.Column(db.Boolean)
    stop_count = db.Column(db.Integer)
    stop_count = db.Column(db.Integer)
    transactions = db.relationship('TxModel', uselist=True,
                                   backref=db.backref('blocks'))

    @classmethod
    def prepare_from_dict(cls, data, **kwargs):
        block_id = int(data.pop('block_id'))
        data.update({'id': block_id})
        header = data.pop('header')
        txs_data = data.pop('transactions')
        h = {}
        for key, val in header.items():
            h['h_' + key] = val
            if key == 'key_id':
                if val:
                    h['h_ukey_id'] = str(int(val) & 0xffffffffffffffff)
                else:
                    h['h_ukey_id'] = '0'
        if 'time' in data:
            time_ts = int(data.pop('time'))
            time_dt = datetime.datetime.fromtimestamp(time_ts)
        else:
            time_ts = 0
            time_dt = datetime.datetime.fromtimestamp(time_ts)
        data['time_ts'] = time_ts
        data['time_dt'] = time_dt
        data.update(h)
        return data, txs_data

    @classmethod
    def update_from_dict(cls, data, **kwargs):
        session = kwargs.get('session', db.session)
        TxModel, ParamModel = get_tx_and_tx_params_models()
        data, txs_data = cls.prepare_from_dict(data)
        block = cls(**data)
        session.add(block)
        txs = []
        for tx_data in txs_data:
            tx = TxModel.update_from_dict(tx_data, session=session,
                                          db_session_commit_enabled=False)
            block.transactions.append(tx)
            txs.append(tx)
        if kwargs.get('db_session_commit_enabled', True):
            session.commit()
        return data, txs

    @classmethod
    def update_from_block(cls, block, **kwargs):
        session = kwargs.get('session', db.session)
        data = block.to_dict(style='snake', struct_style='sqlalchemy')
        if kwargs.get('db_session_commit_enabled', True):
            session.commit()
        return cls.update_from_dict(data, session=session,
        db_session_commit_enabled=kwargs.get('db_session_commit_enabled', True))

    @classmethod
    def update_from_block_set(cls, block_set, **kwargs):
        session = kwargs.get('session', db.session)
        l = []
        for block in block_set.blocks:
            l.append(cls.update_from_block(block, session=session,
                                           db_session_commit_enabled=False))
        #blocks_data = block_set.to_detailed_list(style='snake')
        #l = []
        #for data in blocks_data:
        #    l.append(cls.update_from_dict(data, session=session,
        #                                  db_session_commit_enabled=False))
        if kwargs.get('db_session_commit_enabled', True):
            session.commit()
        return l


