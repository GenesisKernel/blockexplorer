from nose import with_setup

from flask import Flask, current_app

from sqlalchemy.sql.schema import MetaData
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy import exc
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm.session import Session

from genesis_block_explorer.db import db
from genesis_blockchain_api_client.blockchain.block import Block
from genesis_blockchain_api_client.blockchain.block_set import BlockSet
from genesis_blockchain_api_client.blockchain.tx import Tx
from genesis_blockchain_api_client.blockchain.tx_set import TxSet

from genesis_block_explorer.models.db_engine.engine import (
    DbEngineMapIsEmptyError,
)

from genesis_block_explorer.models.genesis.aux.config import (
    update_aux_helpers_bind_name,
)
from genesis_block_explorer.models.genesis.aux.engine import (
    get_aux_helpers_engine,
)
from genesis_block_explorer.models.genesis.aux.session import (
    get_aux_helpers_session
)
from genesis_block_explorer.models.genesis.aux.block import BlockModel
from genesis_block_explorer.models.genesis.aux.block.header import HeaderModel
from genesis_block_explorer.models.genesis.aux.tx.param import ParamModel
from genesis_block_explorer.models.genesis.aux.tx import TxModel
from genesis_block_explorer.models.genesis.aux.tx.helper import (
    TxHelperModel, TxHelperManager, TxHelperManager,
)
from genesis_block_explorer.models.genesis.aux.session import (
    AuxSessionManager, 
)

from .blockchain_commons import d1, d3, d4, get_txs
from .test_models_genesis_aux_block import (
    init_db,
    create_tables,
    create_test_app,
    create_tables_by_seq_nums,
    my_setup,
    my_teardown,
    update_aux_db_engine_discovery_map,
)

seq_nums = (1, ) # 2, 3)
involved_models = [BlockModel, HeaderModel, TxModel,
                   ParamModel]
involved_helpers_models = [TxHelperModel]

def my_setup():
    aux_prefix = 'test_aux_'
    app = create_test_app()
    new_map = update_aux_db_engine_discovery_map(app, force_update=True,
                                       aux_db_engine_name_prefix='test_aux_')
    db.init_app(app)
    with app.app_context():
        init_db()
    create_tables_by_seq_nums(app=app)
    #update_aux_helpers_bind_name(app, prefix='test_')
    engine = get_aux_helpers_engine(app)
    create_tables(involved_helpers_models, engine, recreate_if_exists=True)

@with_setup(my_setup, my_teardown)
def nontest_update_from_main_model_instance():
    app = create_test_app()
    update_aux_db_engine_discovery_map(app, force_update=True,
                                       aux_db_engine_name_prefix='test_aux_')
    engine = get_aux_helpers_engine(app)
    metadata = MetaData()
    metadata.create_all(engine)
    session = get_aux_helpers_session(app)
    create_tables([TxHelperModel], engine, recreate_if_exists=True)
    session.query(TxHelperModel).all()

    sm = AuxSessionManager(app=app)
    seq_num = 1
    bm_session = sm.get(seq_num)
    bm_engine = sm.get_engine(seq_num)
    create_tables([TxModel], bm_engine, recreate_if_exists=True)

    len_bm_first = len(TxModel.query.with_session(bm_session).all())
    assert len_bm_first == 0
    block = Block(b64decode_hashes=True, from_detailed_dict=d3[0])
    BlockModel.update_from_block(block, session=bm_session)
    assert len(BlockModel.query.with_session(bm_session).all()) == len_bm_first + 1

    bm_instance = BlockModel.query.with_session(bm_session).all()[0]

    len_first = len(BlockHelperModel.query.with_session(session).all())
    assert len_first == 0
    BlockHelperModel.update_from_block_model_instance(bm_instance, session=session, block_model_session=bm_session, seq_num=seq_num)
    num_of_bm_fields = len(BlockModel.__table__.columns)
    assert len(BlockHelperModel.query.with_session(session).filter_by(seq_num=seq_num).all()) == len_first + num_of_bm_fields - 1

    BlockHelperModel.query.with_session(session).filter_by(seq_num=seq_num, block_id=bm_instance.id).delete()
    BlockHelperModel.update_from_block_model_instance(bm_instance, session=session, block_model_session=bm_session, seq_num=seq_num)
    assert len(BlockHelperModel.query.with_session(session).filter_by(seq_num=seq_num).all()) == len_first + num_of_bm_fields - 1


@with_setup(my_setup, my_teardown)
def test_tx_helper_manager():
    #app = create_test_app()
    thm = TxHelperManager(engine_echo=False)
    assert len(thm.session.query(thm.model).all()) == 0
    thm.session.add(thm.model(name='Name1', value='Value1'))
    thm.session.add(thm.model(name='Name2', value='Value2'))
    thm.session.commit()
    assert len(thm.session.query(thm.model).all()) == 2
    thm.session.query(thm.model).delete()
    assert len(thm.session.query(thm.model).all()) == 0
    del(thm)

@with_setup(my_setup, my_teardown)
def test_update_from_main_model_instance_via_manager():
    app = create_test_app()
    thm = TxHelperManager(app=app, engine_echo=True)

    sm = AuxSessionManager(app=app)
    seq_num = 1
    tm_session = sm.get(seq_num)
    tm_engine = sm.get_engine(seq_num)
    create_tables([TxModel], tm_engine, recreate_if_exists=True)

    len_tm_first = len(TxModel.query.with_session(tm_session).all())
    assert len_tm_first == 0
    tx = Tx(b64decode_hashes=True, from_detailed_dict=d3[0])
    TxModel.update_from_tx(tx, session=tm_session)
    assert len(TxModel.query.with_session(tm_session).all()) == len_tm_first + 1

    tm_instance = TxModel.query.with_session(tm_session).all()[0]

    len_first = len(thm.session.query(thm.model).all())
    assert len_first == 0
    thm.model.update_from_main_model_instance(tm_instance, session=thm.session, main_model_session=tm_session, seq_num=seq_num)
    num_of_thm_records = len(TxModel.__table__.columns) - len(TxHelperModel.get_drop_fields())
    assert len(thm.session.query(thm.model).all()) == len_first + num_of_thm_records

    thm.session.query(thm.model).filter_by(seq_num=seq_num, hash=tm_instance.hash).delete()
    thm.model.update_from_main_model_instance(tm_instance, session=thm.session, main_model_session=tm_session, seq_num=seq_num)
    assert len(thm.session.query(thm.model).all()) == len_first + num_of_thm_records

