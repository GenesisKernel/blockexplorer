from flask import current_app as app

from genesis_blockchain_api_client.blockchain.block import (
    Block, get_block_id_from_dict, get_block_data_from_dict
)
from genesis_blockchain_api_client.blockchain.block_set import BlockSet
from genesis_blockchain_api_client.blockchain.tx import Tx
from genesis_blockchain_api_client.blockchain.tx_set import TxSet
from genesis_blockchain_api_client.blockchain.tx.param import Param
from genesis_blockchain_api_client.blockchain.tx.param_set import ParamSet

from ......db import db
from ......logging import get_logger
from ...utils import update_dict_with_key_id, update_dict_with_time

logger = get_logger(app) 

class HeaderModel(db.Model):

    __tablename__ = 'blocks_headers'

    id = db.Column(db.Integer, primary_key=True, comment="Header Record ID")

    # main
    block_id = db.Column(db.Integer, comment="Block ID")
    time_ts = db.Column(db.Integer, comment="Time (Stamp)")
    time_dt = db.Column(db.String, comment="Time")
    time_dtu = db.Column(db.String, comment="Time (UTC)")
    ecosystem_id = db.Column(db.Integer, comment="EcoSystem ID")
    key_id = db.Column(db.BigInteger, comment="Key ID")
    wallet = db.Column(db.String, comment="Wallet")
    node_position = db.Column(db.Integer, comment="Node Position")
    sign = db.Column(db.String, comment="Signature")
    hash = db.Column(db.String, comment="Hash")
    version = db.Column(db.Integer, comment="Block Version")

    @classmethod
    def prepare_from_dict(cls, data, **kwargs):
        data = update_dict_with_key_id(data)
        data = update_dict_with_time(data)
        return data

    @classmethod
    def update_from_dict(cls, data, **kwargs):
        session = kwargs.get('session', db.session)
        data = cls.prepare_from_dict(data)
        logger.debug("data: %s" % data)

        header = cls(**data)
        session.add(header)
        if kwargs.get('db_session_commit_enabled', True):
            session.commit()
        return header

    @classmethod
    def update_from_header(cls, header, **kwargs):
        session = kwargs.get('session', db.session)
        data = header.to_dict(style='snake')
        return cls.update_from_dict(data, session=session,
        db_session_commit_enabled=kwargs.get('db_session_commit_enabled', True))

