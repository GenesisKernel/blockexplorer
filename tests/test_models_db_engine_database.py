from nose import with_setup

from sqlalchemy.engine.base import Engine
from sqlalchemy.orm.session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from flask import Flask, current_app

from genesis_block_explorer.app import create_lean_app as create_app
from genesis_block_explorer.config_utils import AppConfig
from genesis_block_explorer.models.db_engine.session import SessionManager

def create_test_app():
    from genesis_block_explorer.app import create_lean_app as create_app
    app = create_app()
    app.app_context().push()
    return app

app = create_test_app()
test_bind_name = 'test_db_engine'
AppConfig(app).add_prefix_to_param_dict_keys('DB_ENGINE_DISCOVERY_MAP', 'test_')

from genesis_block_explorer.models.db_engine.database import (
    Database, import_data
)
Database.__bind_key__ = test_bind_name

def my_setup():
    pass

def my_teardown():
    pass

@with_setup(my_setup, my_teardown)
def test_database_object_creation():
    assert Database.__bind_key__ == test_bind_name
    d = Database()
    assert d.__bind_key__ == test_bind_name

def get_dbex_engine(**kwargs):
    bind_name = kwargs.get('bind_name', 'test_db_engine')
    engine_options = kwargs.get('engine_options', {})
    assert bind_name in app.config['SQLALCHEMY_BINDS']
    conn_uri = app.config.get('SQLALCHEMY_BINDS').get(bind_name)
    assert conn_uri
    return create_engine(conn_uri, **engine_options)

def get_dbex_session(**kwargs):
    bind_name = kwargs.get('bind_name', 'test_db_engine')
    engine_options = kwargs.get('engine_options', {})
    engine = get_dbex_engine(bind_name=bind_name, engine_option=engine_options)
    session_class = scoped_session(sessionmaker(bind=engine)) 
    return session_class()

@with_setup(my_setup, my_teardown)
def test_get_dbex_engine():
    assert isinstance(get_dbex_engine(), Engine)

@with_setup(my_setup, my_teardown)
def test_get_dbex_session():
    session = get_dbex_session()
    assert isinstance(session, Session)

@with_setup(my_setup, my_teardown)
def test_add_from_engine():
    d = Database()
    d.query.delete()
    assert len(d.query.all()) == 0
    sm = SessionManager(app=app)
    seq_num = 1
    assert isinstance(sm.get(seq_num), Session)
    assert isinstance(sm.get_engine(seq_num), Engine)
    Database.add_from_engine(sm.get_engine(seq_num), app=app)
    assert len(d.query.all()) == 1

@with_setup(my_setup, my_teardown)
def test_add_from_engines():
    d = Database()
    d.query.delete()
    assert len(d.query.all()) == 0
    sm = SessionManager(app=app)
    seq_num = 1
    assert isinstance(sm.get(seq_num), Session)
    assert isinstance(sm.get_engine(seq_num), Engine)
    Database.add_from_engines(app=app)
    assert len(d.query.all()) == len(app.config.get('DB_ENGINE_DISCOVERY_MAP'))

@with_setup(my_setup, my_teardown)
def test_database_import_data():
    d = Database()
    d.query.delete()
    assert len(d.query.all()) == 0
    import_data(app)
    assert len(d.query.all()) == len(app.config.get('DB_ENGINE_DISCOVERY_MAP'))
