from nose import with_setup

from sqlalchemy import exc

from genesis_blockchain_api_client.blockchain.block import (
    Block, get_block_id_from_dict, get_block_data_from_dict
)
from genesis_block_explorer.db import db
from genesis_block_explorer.models.genesis.aux.block import BlockModel

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
def test_update_from_block():
    app = create_test_app()
    assert len(BlockModel.query.all()) == 0
    block = Block(b64decode_hashes=True, from_detailed_dict=d3[0])
    BlockModel.update_from_block(block)
    assert len(BlockModel.query.all()) == 1
    b = BlockModel.query.all()[0]
    assert b.id == int(block.id)
    assert b.hash == block.hash
    assert b.ecosystem_id == block.ecosystem_id
    assert b.node_position == block.node_position
    assert b.key_id == block.key_id
    assert b.tx_count == block.tx_count
    #assert type(b.time_ts) == int
    assert b.rollbacks_hash == block.rollbacks_hash
    assert b.mrkl_root == block.mrkl_root
    assert b.bin_data == block.bin_data
    assert b.sys_update == block.sys_update
    assert b.gen_block == block.gen_block
    assert b.stop_count == block.stop_count
    try:
        BlockModel.update_from_block(block)
    except exc.IntegrityError:
        pass


