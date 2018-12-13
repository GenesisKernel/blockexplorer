from nose import with_setup

from flask import Flask, current_app

from sqlalchemy import exc
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm.session import Session

from genesis_block_explorer.db import db
from genesis_blockchain_api_client.blockchain.block import Block
from genesis_blockchain_api_client.blockchain.block_set import BlockSet

from genesis_block_explorer.models.db_engine.engine import (
    DbEngineMapIsEmptyError,
)

from genesis_block_explorer.models.genesis.aux.config import (
    update_aux_db_engine_discovery_map
)
from genesis_block_explorer.models.genesis.aux.block import BlockModel
from genesis_block_explorer.models.genesis.aux.block.header import HeaderModel
from genesis_block_explorer.models.genesis.aux.tx import TxModel
from genesis_block_explorer.models.genesis.aux.tx.param import ParamModel
from genesis_block_explorer.models.genesis.aux.session import (
    AuxSessionManager, 
)

from .blockchain_commons import d1, d3, d4, get_txs

seq_nums = (1, ) # 2, 3)
involved_models = [BlockModel, HeaderModel, TxModel, ParamModel]

def init_db():
    db.create_all()

def create_test_app():
    from genesis_block_explorer.app import create_lean_app as create_app
    app = create_app()
    app.app_context().push()
    update_aux_db_engine_discovery_map(app, force_update=True,
                                       aux_db_engine_name_prefix='test_aux_')
    return app

def create_tables(models, engine, recreate_if_exists=True):
    for model in models:
        if recreate_if_exists:
            try:
                model.__table__.drop(engine)
            except exc.OperationalError as e:
                pass

        try:
            model.__table__.create(engine)
        except exc.OperationalError as e:
            print("Can'n create table for model %s, error: %s" % (model, e))

def create_tables_by_seq_nums(**kwargs):
    app = kwargs.get('app', create_test_app())
    for seq_num in seq_nums:
        asm = AuxSessionManager(app=app)
        create_tables(involved_models, asm.get_engine(seq_num))

def my_setup():
    aux_prefix = 'test_aux_'
    app = create_test_app()
    new_map = update_aux_db_engine_discovery_map(app, force_update=True,
                                       aux_db_engine_name_prefix='test_aux_')
    db.init_app(app)
    with app.app_context():
        init_db()
    create_tables_by_seq_nums(app=app)

def my_teardown():
    pass

@with_setup(my_setup, my_teardown)
def test_get_bind_name():
    app = create_test_app()
    new_map = update_aux_db_engine_discovery_map(app, force_update=True,
                                       aux_db_engine_name_prefix='test_aux_')
    sm = AuxSessionManager(app=app)
    sn = 1
    if len(app.config['AUX_DB_ENGINE_DISCOVERY_MAP']) == 0:
        try:
            sm.get_bind_name(sn)
        except DbEngineMapIsEmptyError as e:
            print("AUX_DB_ENGINE_DISCOVERY_MAP is empty")
            return
    assert sm.get_bind_name(sn) == tuple(app.config['AUX_DB_ENGINE_DISCOVERY_MAP'].keys())[0]

@with_setup(my_setup, my_teardown)
def test_do_if_locked():
    app = create_test_app()
    new_map = update_aux_db_engine_discovery_map(app, force_update=True,
                                       aux_db_engine_name_prefix='test_aux_')
    sm = AuxSessionManager(app=app)
    sn = 1
    session = sm.get(sn)

@with_setup(my_setup, my_teardown)
def test_update_from_block():
    app = create_test_app()
    new_map = update_aux_db_engine_discovery_map(app, force_update=True,
                                       aux_db_engine_name_prefix='test_aux_')
    sm = AuxSessionManager(app=app)
    sn = 1
    create_tables([BlockModel, HeaderModel, TxModel, ParamModel], sm.get_engine(sn))
    if len(app.config['AUX_DB_ENGINE_DISCOVERY_MAP']) == 0:
        try:
            sm.get(sn)
        except DbEngineMapIsEmptyError as e:
            print("AUX_DB_ENGINE_DISCOVERY_MAP is empty")
            return
    len_first = len(BlockModel.query.with_session(sm.get(sn)).all())
    block = Block(b64decode_hashes=True, from_detailed_dict=d3[0])
    BlockModel.update_from_block(block, session=sm.get(sn))
    try:
        BlockModel.update_from_block(block, session=sm.get(sn))
    except exc.IntegrityError:
        pass

