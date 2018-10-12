from nose import with_setup

from sqlalchemy import exc
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm.session import Session

from genesis_block_explorer.db import db
from genesis_block_explorer.models.genesis.aux.config import (
    update_aux_helpers_bind_name,
)
from genesis_block_explorer.models.genesis.aux.session import (
    AuxSessionManager, 
    get_aux_helpers_session,
)

from .test_models_genesis_aux_block import (
    init_db,
    create_tables,
    create_test_app,
    my_setup,
    my_teardown,
    update_aux_db_engine_discovery_map,
)

@with_setup(my_setup, my_teardown)
def test_get_bind_name():
    app = create_test_app()
    sm = AuxSessionManager(app=app)
    if len(app.config['AUX_DB_ENGINE_DISCOVERY_MAP']) == 0:
        try:
            sm.get_bind_name(1)
        except DbEngineMapIsEmptyError as e:
            print("AUX_DB_ENGINE_DISCOVERY_MAP is empty")
            return
    assert sm.get_bind_name(1) == tuple(app.config['AUX_DB_ENGINE_DISCOVERY_MAP'].keys())[0]

@with_setup(my_setup, my_teardown)
def test_get_engine():
    app = create_test_app()
    sm = AuxSessionManager(app=app)
    if len(app.config['AUX_DB_ENGINE_DISCOVERY_MAP']) == 0:
        try:
            sm.get_engine(1)
        except DbEngineMapIsEmptyError as e:
            print("AUX_DB_ENGINE_DISCOVERY_MAP is empty")
            return
    assert isinstance(sm.get_engine(1), Engine)

@with_setup(my_setup, my_teardown)
def test_get_session():
    app = create_test_app()
    sm = AuxSessionManager(app=app)
    if len(app.config['AUX_DB_ENGINE_DISCOVERY_MAP']) == 0:
        try:
            sm.get_session(1)
        except DbEngineMapIsEmptyError as e:
            print("AUX_DB_ENGINE_DISCOVERY_MAP is empty")
            return
    assert isinstance(sm.get_session(1), Session)
    assert sm.get_session(1) == sm.get_session(1)
    assert sm.get(1) == sm.get(1)
    assert sm.get_session(1) == sm.get(1)

@with_setup(my_setup, my_teardown)
def test_get_aux_helpers_session():
    app = create_test_app()
    update_aux_db_engine_discovery_map(app, force_update=True,
                                       aux_db_engine_name_prefix='test_aux_')
    update_aux_helpers_bind_name(app, prefix='test_')
    session = get_aux_helpers_session(app)
    assert isinstance(session, Session)


