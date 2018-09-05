#import json

#from decimal import Decimal

from sqlalchemy.sql import table, column, select, update, insert

from flask import current_app as app

from genesis_blockchain_api_client.blockchain.block import Block
from genesis_blockchain_api_client.blockchain.block_set import BlockSet

from ....db import db
from ....logging import get_logger
from ....models.db_engine.session import SessionManager
#from ....models.db_engine.engine import merge_two_dicts
from ....utils import is_number, ts_to_fmt_time
from ....blockchain import (
    get_block, get_block_data,
    get_detailed_block, get_detailed_block_data,
)

logger = get_logger(app) 
sm = SessionManager(app=app)

class Error(Exception):
    pass

class BlockModel(db.Model):

    __tablename__ = 'blocks'
    __bind_key__ = 'genesis_aux'
    #__table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)

    #header
    h_time = db.Column(db.Integer)
    h_ecosystem_id = db.Column(db.Integer)
    h_key_id = db.Column(db.Integer)
    h_ukey_id = db.Column(db.Integer)
    h_node_position = db.Column(db.Integer)
    h_sign = db.Column(db.Integer)
    h_hash = db.Column(db.Integer)
    h_version = db.Column(db.Integer)

    # main
    hash = db.Column(db.String)
    ecosystem_id = db.Column(db.Integer)
    node_position = db.Column(db.Integer)
    key_id = db.Column(db.Integer)
    ukey_id = db.Column(db.Integer)
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
    transactions = db.Column(db.String)

    @classmethod
    def update_from_block(cls, block, **kwargs):
        data = block.to_dict(style='snake', struct_style='sqlalchemy')
        block_id = int(data.pop('block_id'))
        data.update({'id': block_id})
        header = data.pop('header')
        txs = data.pop('transactions')
        #print("data: %s" % data)
        #print("txs: %s" % txs)
        #print("header: %s" % header)
        h = {}
        for key, val in header.items():
            h['h_' + key] = val
            if key == 'key_id':
                if val:
                    h['h_ukey_id'] = int(val) & 0xffffffffffffffff
                else:
                    h['h_ukey_id'] = 0
        #print("h: %s" % h)
        if 'time' in data:
            time_ts = data.pop('time')
            time_dt = time_ts
        else:
            time_ts = 0
            time_dt = time_ts
        #data['transactions'] = str(txs)
        list_of_dicts = data
        logger.debug("list_of_dicts: %s" % list_of_dicts)
        i = insert(cls.__table__)
        i = i.values(list_of_dicts)
        db.session.execute(i)
        return list_of_dicts

    @classmethod
    def update_from_block_set(cls, **kwargs):
        pass


