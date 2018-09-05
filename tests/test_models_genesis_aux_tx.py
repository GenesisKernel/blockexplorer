from nose import with_setup

from sqlalchemy import exc

from genesis_blockchain_api_client.blockchain.block import (
    Block, get_block_id_from_dict, get_block_data_from_dict
)
from genesis_blockchain_api_client.blockchain.tx import Tx
from genesis_block_explorer.db import db
from genesis_block_explorer.models.genesis.aux.tx import TxModel

from .blockchain_commons import d1, d3, get_txs

def init_db():
    db.create_all(bind='genesis_aux')

def my_setup():
    init_db()
    create_test_app()

def my_teardown():
    pass

def create_test_app():
    from genesis_block_explorer.app import create_app
    app = create_app()
    app.app_context().push()
    return app

@with_setup(my_setup, my_teardown)
def test_update_from_tx():
    td = get_block_data_from_dict(d3[0])['transactions'][0]
    app = create_test_app()
    assert len(TxModel.query.all()) == 0
    tx = Tx(b64decode_hashes=True, from_dict=td)
    TxModel.update_from_tx(tx)
    assert len(TxModel.query.all()) == 1
    t = TxModel.query.all()[0]
    try:
        TxModel.update_from_tx(tx)
    except exc.IntegrityError:
        pass
