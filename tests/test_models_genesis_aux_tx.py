from nose import with_setup

import datetime 
from sqlalchemy import exc

from genesis_blockchain_api_client.blockchain.block import (
    Block, get_block_id_from_dict, get_block_data_from_dict
)
from genesis_blockchain_api_client.blockchain.tx import Tx
from genesis_blockchain_api_client.blockchain.tx_set import TxSet
from genesis_block_explorer.db import db
from genesis_block_explorer.models.genesis.aux.tx import TxModel

from .blockchain_commons import d1, d3, get_txs

def init_db(bind_key=None):
    if bind_key:
        TxMode.__bind_key__ = bind_key
    db.create_all(bind=bind_key)

def my_setup():
    init_db(bind_key='genesis_aux_test')
    create_test_app()

def my_teardown():
    pass

def create_test_app():
    from genesis_block_explorer.app import create_app
    app = create_app()
    app.app_context().push()
    return app

@with_setup(my_setup, my_teardown)
def test_update_from_dict():
    td = get_block_data_from_dict(d3[0])['transactions'][0]
    len_first = len(TxModel.query.all())
    TxModel.update_from_dict(td)
    assert len(TxModel.query.all()) == len_first + 1

@with_setup(my_setup, my_teardown)
def test_update_from_list_of_dicts():
    td = get_block_data_from_dict(d3[1])['transactions']
    len_first = len(TxModel.query.all())
    TxModel.update_from_list_of_dicts(td)
    assert len(TxModel.query.all()) == len_first + len(td)

@with_setup(my_setup, my_teardown)
def test_update_from_tx():
    td = get_block_data_from_dict(d3[0])['transactions'][0]
    len_first = len(TxModel.query.all())
    print("beginning len of TxModel: %d" % len_first)
    tx = Tx(b64decode_hashes=True, from_dict=td)
    TxModel.update_from_tx(tx)
    assert len(TxModel.query.all()) == len_first + 1

@with_setup(my_setup, my_teardown)
def test_update_from_tx_set():
    td = get_block_data_from_dict(d3[0])['transactions']
    len_first = len(TxModel.query.all())
    tx = TxSet(b64decode_hashes=True, from_list=td)
    TxModel.update_from_tx_set(tx)
    assert len(TxModel.query.all()) == len_first + tx.count
