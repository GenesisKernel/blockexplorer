from nose import with_setup

from genesis_block_explorer.models.genesis.aux.session import (
    AuxSessionManager, 
)

from genesis_block_explorer.models.genesis.aux.block import BlockModel

from genesis_block_explorer.models.genesis.aux.filler import FillerIsLockedError
from genesis_block_explorer.models.genesis.aux.block.filler import BlockFiller

from .test_models_genesis_aux_block import (
    my_setup,
    my_teardown,
    create_tables,
    create_test_app,
    update_aux_db_engine_discovery_map,
)

seq_nums = (1, ) # 2, 3)
involved_models = []

@with_setup(my_setup, my_teardown)
def NOtest_fill_block():
    app = create_test_app()
    new_map = update_aux_db_engine_discovery_map(app, force_update=True,
                                       aux_db_engine_name_prefix='test_aux_')
    sm = AuxSessionManager(app=app)
    seq_num = 1
    f = BlockFiller(app=app, seq_num=seq_num, recreate_tables_if_exist=True,
                    )
    block_id = 1
    f.fill_block(block_id)

@with_setup(my_setup, my_teardown)
def test_fill_all_blocks():
    app = create_test_app()
    new_map = update_aux_db_engine_discovery_map(app, force_update=True,
                                       aux_db_engine_name_prefix='test_aux_')
    sm = AuxSessionManager(app=app)
    seq_num = 1
    f = BlockFiller(app=app, seq_num=seq_num, recreate_tables_if_exist=True,
                    fetch_num_of_blocks=10)
    f.fill_all_blocks()

@with_setup(my_setup, my_teardown)
def NOtest_update():
    app = create_test_app()
    new_map = update_aux_db_engine_discovery_map(app, force_update=True,
                                       aux_db_engine_name_prefix='test_aux_')
    sm = AuxSessionManager(app=app)
    seq_num = 1
    session = sm.get(seq_num)
    f = BlockFiller(app=app, seq_num=seq_num, recreate_tables_if_exist=True,
                    fetch_num_of_blocks=10)
    assert session.query(BlockModel).count() == 0
    block_ids = (1, 2, 3, 4)
    for block_id in block_ids:
        f.fill_block(block_id)
    assert session.query(BlockModel).count() == 4
    f.update()
    assert session.query(BlockModel).count() > 4
    f.update()
    assert session.query(BlockModel).count() > 4

@with_setup(my_setup, my_teardown)
def NOtest_clear():
    app = create_test_app()
    new_map = update_aux_db_engine_discovery_map(app, force_update=True,
                                       aux_db_engine_name_prefix='test_aux_')
    sm = AuxSessionManager(app=app)
    seq_num = 1
    session = sm.get(seq_num)
    f = BlockFiller(app=app, seq_num=seq_num, recreate_tables_if_exist=True,
                    fetch_num_of_blocks=10)
    assert session.query(BlockModel).count() == 0
    f.unlock()
    block_ids = (1, 2, 3, 4)
    for block_id in block_ids:
        f.fill_block(block_id)
    assert session.query(BlockModel).count() == 4
    f.clear()
    assert session.query(BlockModel).count() == 0


