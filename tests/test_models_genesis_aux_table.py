from nose import with_setup

from flask import Flask, current_app

from sqlalchemy import exc
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm.session import Session

from genesis_block_explorer.db import db
from genesis_blockchain_api_client.blockchain.block import Block
from genesis_blockchain_api_client.blockchain.block_set import BlockSet

from genesis_block_explorer.models.genesis.aux.config import (
    update_aux_db_engine_discovery_map, get_num_of_backends
)
from genesis_block_explorer.models.genesis.aux.engine import (
    get_aux_db_engines
)
from genesis_block_explorer.models.genesis.aux.table import (
    create_models_tables_for_engine, TableManager
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

def create_test_app():
    from genesis_block_explorer.app import create_lean_app as create_app
    app = create_app()
    app.app_context().push()
    update_aux_db_engine_discovery_map(app, force_update=True,
                                       aux_db_engine_name_prefix='test_aux_')
    return app

def my_setup():
    app = create_test_app()

def my_teardown():
    pass

@with_setup(my_setup, my_teardown)
def test_create_models_tables_for_engine():
    app = create_test_app()
    models = [BlockModel, HeaderModel, TxModel, ParamModel] 
    for bind_name, engine in get_aux_db_engines(app).items():

        create_models_tables_for_engine(engine, models)
        for model in models:
            assert engine.dialect.has_table(engine, model.__tablename__)

@with_setup(my_setup, my_teardown)
def test_table_manager_object():
    app = create_test_app()
    models = [BlockModel, HeaderModel, TxModel, ParamModel] 
    sm = AuxSessionManager(app=app)
    tm = TableManager(app=app, recreate_if_exists=True)
    tm.create_tables()
    for seq_num in range(1, get_num_of_backends(app) + 1):
        engine = sm.get_engine(seq_num)
        for model in models:
            assert engine.dialect.has_table(engine, model.__tablename__)

