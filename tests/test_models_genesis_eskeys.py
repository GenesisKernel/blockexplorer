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

@with_setup(my_setup, my_teardown)
def test_session_manager():
    pass

@with_setup(my_setup, my_teardown)
def test_keys_class():
    seq_num = 1
    es_model = get_ecosystem_model(backend_features=sm.get_be_features(seq_num))
    keys_model= get_keys_model(backend_features=sm.get_be_features(seq_num))

    e_caught = False
    try:
        keys_model.check_ecosystem()
    except EcosystemIsNotSetError as e:
        e_caught = True
    assert e_caught

    assert keys_model.query.with_session(sm.get(seq_num)).count() \
            >= len(app.config.get('DB_ENGINE_DISCOVERY_MAP'))

@with_setup(my_setup, my_teardown)
def test_ecosystem_class():
    seq_num = 1
    es_model = get_ecosystem_model(backend_features=sm.get_be_features(seq_num))
    assert es_model.query.with_session(sm.get(seq_num)).count() >= 1

@with_setup(my_setup, my_teardown)
def test_ecosystem_and_keys_class():
    seq_num = 1
    es_model = get_ecosystem_model(backend_features=sm.get_be_features(seq_num))
    keys_model= get_keys_model(backend_features=sm.get_be_features(seq_num))
    for es in es_model.query.with_session(sm.get(seq_num)).all():
        keys_model.set_ecosystem(es.id)
        assert keys_model.query.with_session(sm.get(seq_num)).count() \
            >= len(app.config.get('DB_ENGINE_DISCOVERY_MAP'))
        #print("ecosystem: %s keys: %s" % (keys_model.get_ecosystem(), keys_model.query.with_session(sm.get(seq_num)).all()))

@with_setup(my_setup, my_teardown)
def test_ecosystem_and_keys_dynamic_class():
    seq_num = 1
    es_model = get_ecosystem_model(backend_features=sm.get_be_features(1))
    for es in es_model.query.with_session(sm.get(seq_num)).all():
        model = get_ecosystem_model(backend_features=sm.get_be_features(seq_num))
        es = model.query.with_session(sm.get(seq_num)).get_or_404(es.id)
        k_model = get_keys_model(backend_features=sm.get_be_features(seq_num))
        #print("k_model.columns: %s" % k_model.__table__.columns)

@with_setup(my_setup, my_teardown)
def test_ecosystem_and_keys_dynamic_class2():
    seq_num = 1
    es_model = get_ecosystem_model(backend_features=sm.get_be_features(1))
    for es in es_model.query.with_session(sm.get(seq_num)).all():
        model = get_ecosystem_model(backend_features=sm.get_be_features(seq_num))
        es = model.query.with_session(sm.get(seq_num)).get_or_404(es.id)
        k_model = get_keys_model(backend_features=sm.get_be_features(seq_num))
        #print("k_model.columns: %s" % k_model.__table__.columns)
