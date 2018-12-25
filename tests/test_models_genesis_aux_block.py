from nose import with_setup

from flask import Flask, current_app

from sqlalchemy import exc
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm.session import Session

from genesis_blockchain_api_client.blockchain.block import Block
from genesis_blockchain_api_client.blockchain.block_set import BlockSet

from genesis_block_explorer.models.db_engine.engine import (
    DbEngineMapIsEmptyError,
)

from genesis_block_explorer.models.genesis.aux.config import (
    update_aux_db_engine_discovery_map
)

from genesis_block_explorer.models.genesis.aux.block import BlockModel
from genesis_block_explorer.models.genesis.aux.block.error import ErrorModel
from genesis_block_explorer.models.genesis.aux.block.header import HeaderModel
from genesis_block_explorer.models.genesis.aux.tx import TxModel
from genesis_block_explorer.models.genesis.aux.tx.param import ParamModel
from genesis_block_explorer.models.genesis.aux.session import (
    AuxSessionManager, 
)

from .blockchain_commons import d1, d3, d4, get_txs

from .utils import common_setup, create_test_app, my_teardown

seq_nums = (1, ) # 2, 3)
involved_models = [BlockModel, HeaderModel, TxModel, ParamModel, ErrorModel]

def my_setup():
    common_setup(seq_nums=seq_nums, involved_models=involved_models)

def my_setup_no_drop():
    common_setup(seq_nums=seq_nums, involved_models=involved_models,
                 recreate_if_exists=False)

@with_setup(my_setup, my_teardown)
def test_add_remove():
    app = create_test_app()
    sm = AuxSessionManager(app=app)
    sn = 1
    session = sm.get(sn)
    assert session.query(BlockModel).count() == 0
    assert session.query(HeaderModel).count() == 0
    assert session.query(TxModel).count() == 0
    assert session.query(ParamModel).count() == 0
    assert session.query(ErrorModel).count() == 0
    block = Block(b64decode_hashes=True, from_detailed_dict=d3[0])
    block_m = BlockModel.update_from_block(block, session=sm.get(sn))
    assert isinstance(block_m, BlockModel)
    assert session.query(BlockModel).count() == 1
    assert session.query(HeaderModel).count() == 1
    assert session.query(TxModel).count() == 2
    assert session.query(ParamModel).count() == 4
    assert session.query(ErrorModel).count() == 0
    block_m.add_error(error="Test Error", raw_error="Test Raw Error")
    assert session.query(ErrorModel).count() == 1
    block_m.delete(session=session)
    assert session.query(BlockModel).count() == 0
    assert session.query(HeaderModel).count() == 0
    assert session.query(TxModel).count() == 0
    assert session.query(ParamModel).count() == 0
    assert session.query(ErrorModel).count() == 0

@with_setup(my_setup_no_drop, my_teardown)
def test_add_clear():
    app = create_test_app()
    sm = AuxSessionManager(app=app)
    sn = 1
    session = sm.get(sn)
    assert session.query(BlockModel).count() == 0
    assert session.query(HeaderModel).count() == 0
    assert session.query(TxModel).count() == 0
    assert session.query(ParamModel).count() == 0
    assert session.query(ErrorModel).count() == 0
    block1 = Block(b64decode_hashes=True, from_detailed_dict=d3[0])
    block1_m = BlockModel.update_from_block(block1, session=sm.get(sn))
    block2 = Block(b64decode_hashes=True, from_detailed_dict=d3[1])
    block2_m = BlockModel.update_from_block(block2, session=sm.get(sn))
    assert isinstance(block1_m, BlockModel)
    assert isinstance(block2_m, BlockModel)
    assert block1_m != block2_m
    assert session.query(BlockModel).count() == 2
    assert session.query(HeaderModel).count() == 2
    assert session.query(TxModel).count() == 4
    assert session.query(ParamModel).count() == 8
    assert session.query(ErrorModel).count() == 0
    block1_m.add_error(error="Test 1 Error", raw_error="Test 1 Raw Error")
    assert session.query(ErrorModel).count() == 1
    block2_m.add_error(error="Test 2 Error", raw_error="Test 2 Raw Error")
    assert session.query(ErrorModel).count() == 2
    BlockModel.clear(session=session)
    assert session.query(BlockModel).count() == 0
    assert session.query(HeaderModel).count() == 0
    assert session.query(ParamModel).count() == 0
    assert session.query(TxModel).count() == 0
    assert session.query(ErrorModel).count() == 0
    

@with_setup(my_setup, my_teardown)
def NOtest_get_bind_name():
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
def NOtest_do_if_locked():
    app = create_test_app()
    new_map = update_aux_db_engine_discovery_map(app, force_update=True,
                                       aux_db_engine_name_prefix='test_aux_')
    sm = AuxSessionManager(app=app)
    sn = 1
    session = sm.get(sn)

@with_setup(my_setup, my_teardown)
def NOtest_update_from_block():
    app = create_test_app()
    new_map = update_aux_db_engine_discovery_map(app, force_update=True,
                                       aux_db_engine_name_prefix='test_aux_')
    sm = AuxSessionManager(app=app)
    sn = 1
    #create_tables([BlockModel, HeaderModel, TxModel, ParamModel], sm.get_engine(sn))
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

@with_setup(my_setup, my_teardown)
def NOtest_add_fill_error():
    app = create_test_app()
    sm = AuxSessionManager(app=app)
    sn = 1
    len_first = BlockModel.query.with_session(sm.get(sn)).count()
    block_id = tuple(d3[0].keys())[0]
    BlockModel.add_fill_error(block_id, session=sm.get(sn))
    len_after = BlockModel.query.with_session(sm.get(sn)).count()

