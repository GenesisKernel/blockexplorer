from nose import with_setup

from sqlalchemy import exc, inspect

from genesis_blockchain_api_client.blockchain.block import (
    Block, get_block_id_from_dict, get_block_data_from_dict
)
from genesis_blockchain_api_client.blockchain.block_set import BlockSet
from genesis_block_explorer.db import db
from genesis_block_explorer.models.genesis.aux.block import BlockModel

from .blockchain_commons import d1, d3, d4, get_txs

BlockModel.__bind_key__ = 'genesis_aux_test'

def init_db(bind_key=None):
    if bind_key:
        BlockModel.__bind_key__ = bind_key
    print("STARTING create all")
    db.create_all(bind=bind_key)

def create_test_app():
    from genesis_block_explorer.app import create_app
    app = create_app()
    app.app_context().push()
    return app

def my_setup():
    bind_key = 'genesis_aux_test'
    app = create_test_app()
    db.init_app(app)
    init_db(bind_key=bind_key)

def my_teardown():
    pass

@with_setup(my_setup, my_teardown)
def test_create_all():
    print("STARTING test_create_all")
    assert BlockModel.__bind_key__ == 'genesis_aux_test'
    db.create_all(bind='genesis_aux_test')
    #bind_name conn_uri = app.config['SQLALCHEMY_DATABASE_URI']
    #conn_uri = app.config['SQLALCHEMY_BINDS'][bind_name]
    #engines[bind_name] = create_engine(conn_uri, **engine_options)
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    print("tables: %s" % tables)
    assert 'blocks' in tables

@with_setup(my_setup, my_teardown)
def nontest_update_from_block():
    len_first = len(BlockModel.query.all())
    block = Block(b64decode_hashes=True, from_detailed_dict=d3[0])
    BlockModel.update_from_block(block)
    try:
        BlockModel.update_from_block(block)
    except exc.IntegrityError:
        pass

@with_setup(my_setup, my_teardown)
def nontest_update_from_block_set():
    len_first = len(BlockModel.query.all())
    block_set = BlockSet(b64decode_hashes=True, from_detailed_dict=d4)
    BlockModel.update_from_block_set(block_set)
    try:
        BlockModel.update_from_block_set(block_set)
    except exc.IntegrityError:
        pass

