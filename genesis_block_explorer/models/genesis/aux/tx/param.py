from sqlalchemy.sql import table, column, select, update, insert

from flask import current_app as app

from genesis_blockchain_api_client.blockchain.block import (
    Block, get_block_id_from_dict, get_block_data_from_dict
)
from genesis_blockchain_api_client.blockchain.block_set import BlockSet
from genesis_blockchain_api_client.blockchain.tx import Tx
from genesis_blockchain_api_client.blockchain.tx_set import TxSet
from genesis_blockchain_api_client.blockchain.tx.param import Param
from genesis_blockchain_api_client.blockchain.tx.param_set import ParamSet

from .....db import db
from .....logging import get_logger
from .....utils import is_number, ts_to_fmt_time
from .....blockchain import (
    get_block, get_block_data,
    get_detailed_block, get_detailed_block_data,
)

logger = get_logger(app) 

class ParamModel(db.Model):

    __tablename__ = 'tx_params'

    id = db.Column(db.Integer, primary_key=True)
    tx_id = db.Column(db.Integer, db.ForeignKey('transactions.id'))

    # main
    name = db.Column(db.String)
    value = db.Column(db.Text)

    @classmethod
    def update_from_dict(cls, data, **kwargs):
        session = kwargs.get('session', db.session)
        param = cls(**data)
        session.add(param)
        if kwargs.get('db_session_commit_enabled', True):
            session.commit()
        return param

    @classmethod
    def update_from_param(cls, param, **kwargs):
        session = kwargs.get('session', db.session)
        data = {'name': param.oname, 'value': param.value}
        return cls.update_from_dict(data,
        db_session_commit_enabled=kwargs.get('db_session_commit_enabled', True))

    @classmethod
    def update_from_param_set(cls, param_set, **kwargs):
        session = kwargs.get('session', db.session)
        list_of_dicts = param_set.to_list(style='camel')
        l= []
        for data in list_of_dicts:
            l.append(cls.update_from_dict(data,
                                          db_session_commit_enabled=False))
        if kwargs.get('db_session_commit_enabled', True):
            session.commit()
        return l


