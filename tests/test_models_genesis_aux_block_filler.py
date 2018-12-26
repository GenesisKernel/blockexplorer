from nose import with_setup

from genesis_block_explorer.models.genesis.aux.session import (
    AuxSessionManager, 
)

from genesis_block_explorer.models.genesis.aux.block import BlockModel

from genesis_block_explorer.models.genesis.aux.filler import FillerIsLockedError
from genesis_block_explorer.models.genesis.aux.block.filler import (
    BlockFiller, get_max_block_id,
)

from .utils import (
    common_setup, create_test_app, my_teardown,
    update_aux_db_engine_discovery_map,
)

seq_nums = (1, ) # 2, 3)
involved_models = [BlockModel]

def my_setup_empty():
    pass

def my_setup():
    common_setup(seq_nums=seq_nums, involved_models=involved_models)

def my_setup_no_drop():
    common_setup(seq_nums=seq_nums, involved_models=involved_models,
                 recreate_if_exists=False)

@with_setup(my_setup, my_teardown)
def test_fill_blocks__1():
    app = create_test_app()
    sm = AuxSessionManager(app=app)
    seq_num = 1
    session = sm.get(seq_num)
    f = BlockFiller(app=app, seq_num=seq_num, recreate_tables_if_exist=False,
                    fetch_num_of_blocks=15)
    assert session.query(BlockModel).count() == 0
    f.fill_blocks(1, 10)
    assert session.query(BlockModel).count() == 10

@with_setup(my_setup_no_drop, my_teardown)
def test_fill_blocks__2():
    app = create_test_app()
    sm = AuxSessionManager(app=app)
    seq_num = 1
    session = sm.get(seq_num)
    BlockModel.clear(session=session)
    assert session.query(BlockModel).count() == 0
    f = BlockFiller(app=app, seq_num=seq_num, recreate_tables_if_exist=False,
                    fetch_num_of_blocks=15)
    f.fill_blocks(1, 35)
    assert session.query(BlockModel).count() == 35

@with_setup(my_setup_no_drop, my_teardown)
def test_fill_blocks__3():
    app = create_test_app()
    sm = AuxSessionManager(app=app)
    seq_num = 1
    session = sm.get(seq_num)
    BlockModel.clear(session=session)
    assert session.query(BlockModel).count() == 0
    f = BlockFiller(app=app, seq_num=seq_num, recreate_tables_if_exist=False,
                    fetch_num_of_blocks=15)
    f.fill_blocks(1, 1000)
    assert session.query(BlockModel).count() == get_max_block_id(seq_num)

@with_setup(my_setup_no_drop, my_teardown)
def test_fill_blocks__4():
    app = create_test_app()
    sm = AuxSessionManager(app=app)
    seq_num = 1
    session = sm.get(seq_num)
    BlockModel.clear(session=session)
    assert session.query(BlockModel).count() == 0
    f = BlockFiller(app=app, seq_num=seq_num, recreate_tables_if_exist=False,
                    fetch_num_of_blocks=15)
    f.fill_blocks(1, 1)
    assert session.query(BlockModel).count() == 1

@with_setup(my_setup_no_drop, my_teardown)
def test_fill_block():
    app = create_test_app()
    sm = AuxSessionManager(app=app)
    seq_num = 1
    session = sm.get(seq_num)
    BlockModel.clear(session=session)
    assert session.query(BlockModel).count() == 0
    f = BlockFiller(app=app, seq_num=seq_num, recreate_tables_if_exist=False)
    block_id = 3
    f.fill_block(block_id)
    assert session.query(BlockModel).count() == 1

@with_setup(my_setup_no_drop, my_teardown)
def test_fill_all_blocks():
    app = create_test_app()
    sm = AuxSessionManager(app=app)
    seq_num = 1
    session = sm.get(seq_num)
    BlockModel.clear(session=session)
    assert session.query(BlockModel).count() == 0
    f = BlockFiller(app=app, seq_num=seq_num, recreate_tables_if_exist=False,
                    fetch_num_of_blocks=10)
    f.fill_all_blocks()
    assert session.query(BlockModel).count() == get_max_block_id(seq_num)

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


