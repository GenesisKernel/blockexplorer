from nose import with_setup

from sqlalchemy import exc

from genesis_block_explorer.db import db
from genesis_block_explorer.models.genesis.aux.engine import (
    get_aux_db_engines,
    get_aux_db_engine_info,
)

def init_db(bind_key=None):
    if bind_key:
        pass
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
def test_get_aux_db_engines():
    app = create_test_app()
    engines = get_aux_db_engines(app)
    print("engines: %s" % engines)
    assert engines

@with_setup(my_setup, my_teardown)
def test_get_aux_db_engine_info():
    app = create_test_app()
    engines = get_aux_db_engines(app)
    assert engines
    info = get_aux_db_engine_info('genesis_aux_test')
    print("info: %s" % info)
    assert info
