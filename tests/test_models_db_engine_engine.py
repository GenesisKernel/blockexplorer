from nose import with_setup

from sqlalchemy.engine.base import Engine

from flask import Flask, current_app

from genesis_block_explorer.app import create_lean_app as create_app

def create_test_app():
    from genesis_block_explorer.app import create_lean_app as create_app
    app = create_app()
    app.app_context().push()
    return app

app = create_test_app()

from genesis_block_explorer.models.db_engine.engine import (
    get_discovered_db_engines,
)

def my_setup():
    pass

def my_teardown():
    pass

@with_setup(my_setup, my_teardown)
def test_get_discovered_db_engines():
    engines = get_discovered_db_engines(app)
    assert type(engines) == dict
    assert len(engines) == len(app.config.get('DB_ENGINE_DISCOVERY_MAP'))
    for bind_name, backend_version \
            in app.config.get('DB_ENGINE_DISCOVERY_MAP').items():
        assert bind_name in engines
        assert isinstance(engines[bind_name], Engine)


