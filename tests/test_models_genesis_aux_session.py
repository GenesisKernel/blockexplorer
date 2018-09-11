from nose import with_setup

from sqlalchemy import exc
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm.session import Session

from genesis_block_explorer.db import db
from genesis_block_explorer.models.genesis.aux.session import (
    AuxSessionManager, 
    DbEngineMapIsEmptyError
)

def init_db(bind_key=None):
    if bind_key:
        pass
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

