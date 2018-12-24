import json

from decimal import Decimal

from sqlalchemy.sql import table, column, select, update, insert

from flask import current_app as app

from ...db import db
from ...logging import get_logger
from ...models.db_engine.session import SessionManager
from ...models.db_engine.engine import merge_two_dicts
from ...utils import is_number, ts_to_fmt_time
from ...blockchain import (
    get_block, get_block_data,
    get_detailed_block, get_detailed_block_data,
)

from .explicit import get_sys_param_model, BlockChain, TransactionsStatus

from genesis_block_chain.parser.common_parse_data_full import parse_block
from genesis_block_chain.parser.common import Parser

from .block_utils import (
    BlockRows, BlockItem, PAttr, PBDKey, PTxExtraKey, PTxAttr, PTxSmartKey,
    TransactionRows, TxItem,
    create_time_items,
    ItemCreationError,
    BlockTransactionRows, BlockTxItem,
)

logger = get_logger(app) 
sm = SessionManager(app=app)

class Error(Exception):
    pass

class UnknownFullNodeRecordFormat(Error):
    pass

class UnknownFullNodeRecordRowFormat(Error):
    pass

def parse_full_nodes_rec_row(row):
    tcp_address = ""
    tcp_port = ""
    api_url = ""
    key_id = ""
    public_key = ""
    if isinstance(row, list):
        if len(row) == 3:
            # version 1
            tcp_address = row[0]
            key_id = row[1]
            public_key = row[2]
        else:
            raise UnknownFullNodeRecordRowFormat(
                    "list of len expeted 3 but len is %d, row: %s" \
                        % (len(row), row))
    elif isinstance(row, dict):
        # version 2
        if 'tcp_address' in row:
            tcp_address = row['tcp_address']
        else:
            logger.warning("tcp_address key doesn't exist")
        if 'key_id' in row:
            key_id = row['key_id']
        else:
            logger.warning("tcp_address key doesn't exist")
        if 'public_key' in row:
            public_key = row['public_key']
        else:
            logger.warning("tcp_address key doesn't exist")
        if 'api_address' in row:
            api_url = row['api_address']
        elif 'api_url' in row:
            api_url = row['api_url']
        else:
            logger.warning("api_address or api_url key doesn't exist")
    else:
        raise UnknownFullNodeRecordRowFormat(
                "list or dict expected but type is: %s, row: %s" \
                        % (type(row), row))
        
    tcp_address_l = tcp_address.split(':')
    tcp_address = tcp_address_l[0]
    if len(tcp_address_l) > 1:
        tcp_port = tcp_address_l[1]
    else:
        tcp_port = ""
    logger.debug(
            ("tcp_address: %s tcp_port: %s api_url: %s" \
            + " key_id: %s public_key: %s")
            % (tcp_address, tcp_port, api_url, key_id, public_key))
    return dict(tcp_address=tcp_address, tcp_port=tcp_port,
                api_url=api_url, key_id=key_id, public_key=public_key)

def parse_full_nodes_rec(rec, add_db_id=None):
    data = []
    if rec:
        rec = json.loads(rec)
        if not isinstance(rec, list):
            raise UnknownFullNodeRecordFormat("list expected, but it's a %s" \
                                        % type(rec))
        for row in rec:
            parsed = parse_full_nodes_rec_row(row)
            if add_db_id:
                parsed['db_id'] = add_db_id
            data.append(parsed)
    return data 

class FullNode(db.Model):

    __tablename__ = 'full_nodes'
    __bind_key__ = 'genesis_helpers'

    id = db.Column(db.Integer, primary_key=True)
    db_id = db.Column(db.Integer)
    tcp_address = db.Column(db.String)
    tcp_port = db.Column(db.String)
    api_url = db.Column(db.String)
    key_id = db.Column(db.BigInteger)
    public_key = db.Column(db.String)

    @classmethod
    def update_from_sys_param(cls, db_id=1):
        model = get_sys_param_model(backend_features=sm.get_be_features(db_id))
        data = model.query.with_session(sm.get(db_id)).filter_by(name='full_nodes').one().value
        data = parse_full_nodes_rec(data, add_db_id=db_id)
        logger.debug("FULL NODES DDDDDDDDDDDDAATA: %s" % data)
        cls.query.filter_by(db_id=db_id)
        i = insert(cls.__table__)
        i = i.values(data)
        db.session.execute(i)

class BlockHelper(db.Model):

    __tablename__ = 'block_helper'
    __bind_key__ = 'genesis_helpers'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    db_id = db.Column(db.Integer)
    block_id = db.Column(db.Integer)
    name = db.Column(db.String)
    title = db.Column(db.String)
    src = db.Column(db.String)
    value = db.Column(db.Text)
    type = db.Column(db.String)
    raw = db.Column(db.Boolean)

    @classmethod
    def update_from_block_chain(cls, **kwargs):
        db_id = kwargs.get('db_id', 1)
        block_id = kwargs.get('block_id', 1)
        show_raw_data = kwargs.get('show_raw_data', False)
        block = BlockChain.query.with_session(sm.get(db_id)).filter_by(id=block_id).one()

        d_names_titles = {
            'hash': 'Hash',
            'rollbacks_hash': 'Rollbacks Hash',
            'data': 'Raw Block Data',
            'ecosystem_id': 'Ecosystem ID',
            'node_position': 'Node Position',
            'time': 'Time'
        }

        r = BlockRows(db_id=db_id, block_id=block_id)

        p_data = None
        for col_name, col_title in d_names_titles.items():
            val = getattr(block, col_name)
            if col_name in ['hash', 'rollbacks_hash']:
                r.add(BlockItem(col_name, val.hex(), a="d 0 str", t=col_title))
            elif col_name in ['ecosystem_id', 'node_position', 'tx']:
                r.add(BlockItem(col_name, val, a="d 0 int", t=col_title))
            elif col_name in ['time']:
                [r.add(t) for t in create_time_items(BlockItem,
                                          col_name, val, a_s="d", t=col_title)]
            elif col_name in ['data']:
                p_data = val
            else:
                r.add(BlockItem(col_name, str(val), a="d 1 str", t=col_title))

        if p_data:
            b_names_titles = {
                # block data
                'block_id': 'Block ID',
                'block_version': 'Block Version',
                'block_time': 'Block Time',
                'ecosystem_id': 'Ecosystem ID',
                'node_position': 'Node Position',
                'sign': 'Sign',

                # tx
                'tx_type': 'Transaction Type ID',
                'tx_type_str': 'Transaction Type',
                'tx_hash': 'Transaction Hash',
                'tx_user_cost': 'Transaction User Cost',
                'tx_ecosystem_id': 'Transaction Ecosystem ID',
                'tx_contract': 'Transaction Contract',
                'tx_data': 'Transaction Data',
                'public_key': 'Public Key',
                'bin_signatures': 'Binary Signatures',
                'token_ecosystem': 'Token Ecosystem',
                'signed_by': 'Signed By',
                'max_sum': 'Max Sum',
                'pay_over': 'Pay Over',
                'request_id': 'Request ID',
                # tx extra
                'tx_size': 'Transaction Size',
                'tx_size_offset': 'Transaction Size Offset',
            }
            try:
                p = parse_block(p_data)
            except Exception as e:
                logger.error("Block Parse Error: %s" % e)
                p = Parser()
        else:
            b_names_titles = {}

        # common part for blocks of all kinds tx
        for col_name, col_title in b_names_titles.items():
            if col_name in ['block_id', 'block_version', 'ecosystem_id',
                            'node_position']: 
                r.add(PBDKey(col_name, p, a="b 0 int", t=col_title))
            elif col_name in ['sign']:
                r.add(PBDKey(col_name, p, a="b 0 str", t=col_title))
            elif col_name in ['tx_hash', 'tx_type_str', 'public_key']:
                r.add(PAttr(col_name, p, a="b 0 str", t=col_title))
            elif col_name in ['block_time']:
                [r.add(t) for t in create_time_items(PBDKey,
                                    col_name, p, a_s="b", t=col_title)]
            elif col_name in ['tx_data']:
                r.add(PAttr(col_name, p, a="b 0 str", t=col_title))
            #elif col_name in ['tx_ecosystem_id', 'tx_type']:
            elif col_name in ['tx_type']:
                r.add(PAttr(col_name, p, a="b 0 int", t=col_title))
            elif col_name in ['tx_size', 'tx_size_offset']:
                r.add(PTxExtraKey(col_name, p, a="b 0 int", t=col_title))

        # tx specific part
        if hasattr(p, 'tx_type_str'):
            logger.debug("block tx type: %s" % p.tx_type_str)
            if p.tx_type_str == 'contract':
                for col_name, col_title in b_names_titles.items():
                    if col_name in ['tx_contract']:
                        r.add(PAttr(col_name, p, a="b 0 str", t=col_title))
                    elif col_name in ['bin_signatures', 'token_ecosystem',
                                      'pay_over', 'max_sum', 'request_id',]:
                        r.add(PTxSmartKey(col_name, p, a="b 0 str",
                                          t=col_title))
                    elif col_name in ['signed_by', 'token_ecosystem']:
                        r.add(PTxSmartKey(col_name, p, a="b 0 int",
                                          t=col_title))
                    #elif col_name in ['tx_user_cost']:
                    #    r.add(PAttr(col_name, p, a="b 0 dec", t=col_title))
                    elif col_name in ['tx_ecosystem_id', 'tx_type']:
                        r.add(PAttr(col_name, p, a="b 0 int", t=col_title))
                    if col_name in ['ecosystem_id']:
                        r.add(PTxSmartKey(col_name, p, a="b 0 int",
                                          t=col_title))
            elif p.tx_type_str == 'structure':
                pass
            else:
                pass
        else:
            logger.warning("block tx type str not found")

        r.consolidate()
        list_of_dicts = r.to_list_of_dicts()
        cls.query.filter_by(db_id=db_id, block_id=block_id)
        i = insert(cls.__table__)
        i = i.values(list_of_dicts)
        db.session.execute(i)
        return list_of_dicts

class BlockTransactionsHelper(db.Model):

    __tablename__ = 'block_transactions_helper'
    __bind_key__ = 'genesis_helpers'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    db_id = db.Column(db.Integer)
    block_id = db.Column(db.Integer)
    time = db.Column(db.Integer)
    type = db.Column(db.Integer)
    key_id = db.Column(db.String)
    hash = db.Column(db.String)
    contract_name = db.Column(db.String)
    params = db.Column(db.String)

    @classmethod
    def update_from_block(cls, **kwargs):
        db_id = kwargs.get('db_id', 1)
        block_id = kwargs.get('block_id', '')
        data = get_detailed_block(db_id, block_id).to_dict(style='snake',
                                                  struct_style='sqlalchemy') 
        #data = get_block(db_id, block_id).to_dict(style='snake',
        #                                          struct_style='sqlalchemy') 
        list_of_dicts = []
        if 'transactions' in data:
            for tx in data['transactions']:
                d = {'db_id': db_id, 'block_id': block_id}
                #tx['hash'] = tx['hash'][:].encode().hex()
                tx['params'] = str(tx['params'])
                d.update(tx)
                list_of_dicts.append(d)
        logger.debug("list_of_dicts: %s" % list_of_dicts)

        i = insert(cls.__table__)
        i = i.values(list_of_dicts)
        db.session.execute(i)
        return list_of_dicts

class TransactionStatusHelper(db.Model):

    __tablename__ = 'transaction_helper'
    __bind_key__ = 'genesis_helpers'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    db_id = db.Column(db.Integer)
    tx_hash = db.Column(db.String)
    name = db.Column(db.String)
    title = db.Column(db.String)
    src = db.Column(db.String)
    value = db.Column(db.Text)
    type = db.Column(db.String)
    raw = db.Column(db.Boolean)

    @classmethod
    def update_from_transactions_status(cls, **kwargs):
        db_id = kwargs.get('db_id', 1)
        tx_hash = kwargs.get('tx_hash', '')
        show_raw_data = kwargs.get('show_raw_data', False)
        tx_hash_b = bytes.fromhex(tx_hash)
        tx = TransactionsStatus.query.with_session(sm.get(db_id)).filter(TransactionsStatus.hash==tx_hash_b).one()

        d_names_titles = {
            'time': 'Time',
            'hash': 'Hash',
            'ecosystem': 'Ecosystem ID',
            'block_id': 'Block ID',
            'key_id': 'Sender Key ID',
            'error': 'Error',
        }
        r = TransactionRows(db_id=db_id, tx_hash=tx_hash)

        p_data = None
        for col_name, col_title in d_names_titles.items():
            val = getattr(tx, col_name)
            if col_name in ['ecosystem', 'key_id', 'block_id']:
                r.add(TxItem(col_name, val, a="d 0 int", t=col_title))
            elif col_name in ['error']:
                r.add(TxItem(col_name, val, a="d 0 str", t=col_title))
            elif col_name in ['hash']:
                r.add(TxItem(col_name, tx_hash, a="d 0 str", t=col_title))
            elif col_name in ['time']:
                [r.add(t) for t in create_time_items(TxItem,
                                          col_name, val, a_s="d", t=col_title)]
            else:
                r.add(TxItem(col_name, str(val), a="d 1 str", t=col_title))

        list_of_dicts = r.to_list_of_dicts()
        cls.query.filter_by(db_id=db_id, tx_hash=tx_hash)
        i = insert(cls.__table__)
        i = i.values(list_of_dicts)
        db.session.execute(i)
        return list_of_dicts

def init_db():
    db.create_all(bind='genesis_helpers')
