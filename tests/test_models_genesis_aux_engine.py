from nose import with_setup

from sqlalchemy import exc
from sqlalchemy.engine.base import Engine

from genesis_block_explorer.db import db
from genesis_block_explorer.models.genesis.aux.engine import (
    get_aux_db_engines,
    get_aux_db_engine_info,
    get_aux_helpers_engine,
)
from genesis_block_explorer.models.genesis.aux.config import (
    update_aux_helpers_bind_name,
)
from .test_models_genesis_aux_block import (
    init_db,
    create_tables,
    create_test_app,
    my_setup,
    my_teardown,
    update_aux_db_engine_discovery_map,
)

seq_nums = (1, ) # 2, 3)
involved_models = []

@with_setup(my_setup, my_teardown)
def test_get_aux_db_engines():
    app = create_test_app()
    update_aux_db_engine_discovery_map(app, force_update=True,
                                       aux_db_engine_name_prefix='test_aux_')
    engines = get_aux_db_engines(app)
    assert engines

@with_setup(my_setup, my_teardown)
def test_get_aux_db_engine_info():
    app = create_test_app()
    update_aux_db_engine_discovery_map(app, force_update=True,
                                       aux_db_engine_name_prefix='test_aux_')
    engines = get_aux_db_engines(app)
    assert engines
    info = get_aux_db_engine_info('test_aux_genesis1')
    assert info

@with_setup(my_setup, my_teardown)
def test_get_aux_helpers_engine():
    app = create_test_app()
    update_aux_db_engine_discovery_map(app, force_update=True,
                                       aux_db_engine_name_prefix='test_aux_')
    update_aux_helpers_bind_name(app, prefix='test_')
    engine = get_aux_helpers_engine(app)
    assert isinstance(engine, Engine)
