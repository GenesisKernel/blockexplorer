from nose import with_setup

from sqlalchemy import exc
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm.session import Session

from genesis_block_explorer.db import db
from genesis_block_explorer.models.genesis.aux.config import (
    update_aux_db_engine_discovery_map
)
from genesis_block_explorer.models.genesis.aux.filler import (
    Filler,
)
from genesis_block_explorer.models.genesis.aux.block import BlockModel
from genesis_block_explorer.models.genesis.aux.tx import TxModel
from genesis_block_explorer.models.genesis.aux.tx.param import ParamModel
from genesis_block_explorer.models.genesis.aux.session import (
    AuxSessionManager, 
    DbEngineMapIsEmptyError
)

from .test_models_genesis_aux_block import (
    init_db,
    create_test_app,
    my_setup,
    my_teardown,
)

@with_setup(my_setup, my_teardown)
def test_check_dbs():
    app = create_test_app()
    new_map = update_aux_db_engine_discovery_map(app, force_update=True,
                                       aux_db_engine_name_prefix='test_aux_')
    f = Filler(app=app)
    f.check_dbs()

@with_setup(my_setup, my_teardown)
def test_fill_block():
    app = create_test_app()
    new_map = update_aux_db_engine_discovery_map(app, force_update=True,
                                       aux_db_engine_name_prefix='test_aux_')
    sm = AuxSessionManager(app=app)
    seq_num = 1
    f = Filler(app=app, seq_num=seq_num, recreate_tables_if_exist=True)
    block_id = 1
    f.fill_block(block_id)

@with_setup(my_setup, my_teardown)
def test_fill_all_blocks():
    app = create_test_app()
    new_map = update_aux_db_engine_discovery_map(app, force_update=True,
                                       aux_db_engine_name_prefix='test_aux_')
    sm = AuxSessionManager(app=app)
    seq_num = 1
    f = Filler(app=app, seq_num=seq_num, recreate_tables_if_exist=True)
    f.fill_all_blocks()

@with_setup(my_setup, my_teardown)
def test_update():
    app = create_test_app()
    new_map = update_aux_db_engine_discovery_map(app, force_update=True,
                                       aux_db_engine_name_prefix='test_aux_')
    sm = AuxSessionManager(app=app)
    seq_num = 1
    f = Filler(app=app, seq_num=seq_num, recreate_tables_if_exist=True)
    block_ids = (1, 2, 3, 4)
    for block_id in block_ids:
        f.fill_block(block_id)
    f.update()


