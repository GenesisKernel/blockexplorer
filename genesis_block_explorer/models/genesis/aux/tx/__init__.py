#import json

#from decimal import Decimal

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

logger = get_logger(app) 
sm = SessionManager(app=app)

class Error(Exception):
    pass

class TxModel(db.Model):

    __tablename__ = 'transactions'
    __bind_key__ = 'genesis_aux'
    #__table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)

    # main
    hash = db.Column(db.String)
    contract_name = db.Column(db.String)
    node_position = db.Column(db.Integer)
    key_id = db.Column(db.Integer)
    ukey_id = db.Column(db.Integer)
    time_ts = db.Column(db.Integer)
    time_dt = db.Column(db.DateTime)
    type = db.Column(db.Integer)
    #params = db.relationship('Param', uselist=True,
    #                         backref=db.backref('transactions'))

    @classmethod
    def update_from_tx(cls, tx, **kwargs):
        data = tx.to_dict(style='snake')
        params = data.pop('params')
        if 'key_id' in data:
            if data['key_id']:
                data['ukey_id'] = int(data['key_id']) & 0xffffffffffffffff
            else:
                data['ukey_id'] = 0
        if 'time' in data:
            time_ts = data.pop('time')
            time_dt = time_ts
        else:
            time_ts = 0
            time_dt = time_ts
        #data['transactions'] = str(txs)
        list_of_dicts = [data]
        logger.debug("list_of_dicts: %s" % list_of_dicts)
        i = insert(cls.__table__)
        i = i.values(list_of_dicts)
        db.session.execute(i)
        return list_of_dicts

    @classmethod
    def update_from_tx_set(cls, tx_set, **kwargs):
        data = tx_set.to_list(style='snake')


