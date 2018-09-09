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
from genesis_blockchain_api_client.blockchain.tx.param import Param
from genesis_blockchain_api_client.blockchain.tx.param_set import ParamSet

from .....db import db
from .....logging import get_logger
from .....models.db_engine.session import SessionManager
from .....utils import is_number, ts_to_fmt_time
from .....blockchain import (
    get_block, get_block_data,
    get_detailed_block, get_detailed_block_data,
)

logger = get_logger(app) 
sm = SessionManager(app=app)

#from . import ParamModel

class ParamModel(db.Model):

    __tablename__ = 'tx_params'
    #__bind_key__ = 'genesis_aux'
    #__table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    tx_id = db.Column(db.Integer, db.ForeignKey('transactions.id'))

    # main
    name = db.Column(db.String)
    value = db.Column(db.Text)

    @classmethod
    def update_from_dict(cls, data):
        list_of_dicts = [data]
        logger.debug("list_of_dicts: %s" % list_of_dicts)
        i = insert(cls.__table__)
        i = i.values(list_of_dicts)
        db.session.execute(i)
        return list_of_dicts

    @classmethod
    def update_from_param(cls, param, **kwargs):
        data = {'name': param.oname, 'value': param.value}
        return cls.update_from_dict(data)

    @classmethod
    def update_from_param_set(cls, param_set, **kwargs):
        list_of_dicts = param_set.to_list(style='camel')
        #for param in data:
        #    cls.update_from_param(param)
        i = insert(cls.__table__)
        i = i.values(list_of_dicts)
        db.session.execute(i)
        return list_of_dicts


