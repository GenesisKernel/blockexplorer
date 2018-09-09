from nose import with_setup

from sqlalchemy import exc

from genesis_blockchain_api_client.blockchain.block import (
    Block, get_block_id_from_dict, get_block_data_from_dict
)
from genesis_blockchain_api_client.blockchain.tx import Tx
from genesis_blockchain_api_client.blockchain.tx.param import Param
from genesis_blockchain_api_client.blockchain.tx.param_set import ParamSet
from genesis_block_explorer.db import db
from genesis_block_explorer.models.genesis.aux.tx import TxModel
from genesis_block_explorer.models.genesis.aux.tx.param import ParamModel

from .blockchain_commons import d1, d3, get_txs

def init_db(bind_key=None):
    if bind_key:
        TxModel.__bind_key__ = bind_key
        ParamModel.__bind_key__ = bind_key
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
def test_update_from_param():
    td = get_block_data_from_dict(d3[0])['transactions'][0]['params'] # [0]
    p0n = tuple(td.keys())[0]
    p0v = td[p0n]
    pd = {p0n: p0v}
    app = create_test_app()
    assert len(ParamModel.query.all()) == 0
    p = Param(**pd)
    ParamModel.update_from_param(p)
    assert len(ParamModel.query.all()) == 1
    pm = ParamModel.query.all()[0]
    print("pm.name: %s, p0n: %s" % (pm.name, p0n))
    assert pm.name == p0n
    assert pm.value == p0v
    try:
        ParamModel.update_from_param(p)
    except exc.IntegrityError:
        pass

@with_setup(my_setup, my_teardown)
def test_update_from_param_set():
    pd = get_block_data_from_dict(d3[0])['transactions'][0]['params']
    assert len(ParamModel.query.all()) == 0
    ps = ParamSet(**pd)
    ParamModel.update_from_param_set(ps)
    assert len(ParamModel.query.all()) == len(pd)
    pm = ParamModel.query.all()[0]
    try:
        ParamModel.update_from_param_set(ps)
    except exc.IntegrityError:
        pass
