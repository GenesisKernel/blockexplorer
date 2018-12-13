from nose import with_setup

from sqlalchemy.engine.base import Engine
from sqlalchemy.orm.session import Session

from flask import Flask, current_app

from genesis_block_explorer.app import create_lean_app as create_app

def create_test_app():
    from genesis_block_explorer.app import create_lean_app as create_app
    app = create_app()
    app.app_context().push()
    return app

app = create_test_app()

from genesis_block_explorer.models.db_engine.session import SessionManager

def my_setup():
    pass

def my_teardown():
    pass

@with_setup(my_setup, my_teardown)
def test_session_manager_object_creation():
    sm = SessionManager(app=app)
    assert len(sm.engines) == len(app.config.get('DB_ENGINE_DISCOVERY_MAP'))
    assert len(sm.sessions) == len(app.config.get('DB_ENGINE_DISCOVERY_MAP'))
    for bind_name, backend_version \
            in app.config.get('DB_ENGINE_DISCOVERY_MAP').items():
        assert bind_name in sm.engines
        assert isinstance(sm.engines[bind_name], Engine)
        assert bind_name in sm.sessions
        assert 'session_class' in sm.sessions[bind_name]
        assert 'session' in sm.sessions[bind_name]
        assert isinstance(sm.sessions[bind_name]['session'], Session)
    print("features: %s" % sm.get_be_features(1))

