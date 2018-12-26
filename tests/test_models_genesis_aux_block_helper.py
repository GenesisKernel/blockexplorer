from nose import with_setup

from flask import Flask, current_app

#from sqlalchemy_dict import BaseModel
##from sqlalchemy import BaseModel
#from sqlalchemy.ext import Base as BaseModel
from sqlalchemy.sql.schema import MetaData
from sqlalchemy.ext.declarative import declarative_base

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
from genesis_block_explorer.models.genesis.aux.block.helper import (
    BlockHelperModel, BlockHelperManager
)
from genesis_block_explorer.models.genesis.aux.tx import TxModel
from genesis_block_explorer.models.genesis.aux.tx.param import ParamModel
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
involved_helpers_models = [BlockHelperModel]

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
def test_block_helper_manager():
    #app = create_test_app()
    bhm = BlockHelperManager(engine_echo=False)
    assert len(bhm.session.query(bhm.model).all()) == 0
    bhm.session.add(bhm.model(name='Name1', value='Value1'))
    bhm.session.add(bhm.model(name='Name2', value='Value2'))
    bhm.session.commit()
    assert len(bhm.session.query(bhm.model).all()) == 2
    bhm.session.query(bhm.model).delete()
    assert len(bhm.session.query(bhm.model).all()) == 0
    del(bhm)

@with_setup(my_setup, my_teardown)
def test_update_from_block_model_instance_via_manager():
    app = create_test_app()
    bhm = BlockHelperManager(app=app, engine_echo=False)

    sm = AuxSessionManager(app=app)
    seq_num = 1
    bm_session = sm.get(seq_num)
    bm_engine = sm.get_engine(seq_num)
    create_tables([BlockModel], bm_engine, recreate_if_exists=True)

    len_bm_first = len(BlockModel.query.with_session(bm_session).all())
    assert len_bm_first == 0
    block = Block(b64decode_hashes=True, from_detailed_dict=d3[0])
    BlockModel.update_from_block(block, session=bm_session)
    assert len(BlockModel.query.with_session(bm_session).all()) == len_bm_first + 1

    bm_instance = BlockModel.query.with_session(bm_session).all()[0]

    len_first = len(bhm.session.query(bhm.model).all())
    assert len_first == 0
    bhm.model.update_from_main_model_instance(bm_instance, session=bhm.session, main_model_session=bm_session, seq_num=seq_num)
    num_of_bhm_records = len(BlockModel.__table__.columns) - len(BlockHelperModel.get_drop_fields()) + 2
    assert len(bhm.session.query(bhm.model).all()) == len_first + num_of_bhm_records 
    bhm.session.query(bhm.model).filter_by(seq_num=seq_num, block_id=bm_instance.id).delete()
    bhm.model.update_from_main_model_instance(bm_instance, session=bhm.session, main_model_session=bm_session, seq_num=seq_num)
    assert len(bhm.session.query(bhm.model).all()) == len_first + num_of_bhm_records

