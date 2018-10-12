from nose import with_setup

from flask import Flask, current_app

from genesis_block_explorer.app import create_lean_app as create_app
#from genesis_block_explorer.app import create_app

from .blockchain_commons import d1, d3, get_txs
from .test_models_genesis_aux_block import (
    my_setup,
    my_teardown,
    create_tables,
    create_test_app,
    update_aux_db_engine_discovery_map,
)

seq_nums = (1, ) # 2, 3)
involved_models = []
app = create_test_app()
update_aux_db_engine_discovery_map(app, force_update=True,
                                   aux_db_engine_name_prefix='test_aux_')

from genesis_block_explorer.models.db_engine.session import SessionManager
from genesis_block_explorer.models.genesis.explicit import (
    get_ecosystem_model, get_keys_model, 
    EcosystemIsNotSetError,
)

sm = SessionManager(app=app)
EsKeys = get_keys_model(backend_features=sm.get_be_features(1))
Ecosystem = get_ecosystem_model(backend_features=sm.get_be_features(1))

@with_setup(my_setup, my_teardown)
def test_session_manager():
    pass

@with_setup(my_setup, my_teardown)
def test_keys_class():
    seq_num = 1

    e_caught = False
    try:
        EsKeys.check_ecosystem()
    except EcosystemIsNotSetError as e:
        e_caught = True
    assert e_caught

    assert len(EsKeys.query.with_session(sm.get(seq_num)).all()) \
            >= len(app.config.get('DB_ENGINE_DISCOVERY_MAP'))

@with_setup(my_setup, my_teardown)
def test_ecosystem_class():
    seq_num = 1
    assert len(Ecosystem.query.with_session(sm.get(seq_num)).all()) >= 1

@with_setup(my_setup, my_teardown)
def test_ecosystem_and_keys_class():
    seq_num = 1
    for es in Ecosystem.query.with_session(sm.get(seq_num)).all():
        EsKeys.set_ecosystem(es.id)
        assert len(EsKeys.query.with_session(sm.get(seq_num)).all()) \
            >= len(app.config.get('DB_ENGINE_DISCOVERY_MAP'))

