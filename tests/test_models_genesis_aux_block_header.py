from nose import with_setup

import datetime 
from sqlalchemy import exc

from genesis_blockchain_api_client.blockchain.block import (
    Block, get_block_id_from_dict, get_block_data_from_dict
)
from genesis_blockchain_api_client.blockchain.block.header import Header

from genesis_block_explorer.db import db

from genesis_block_explorer.models.db_engine.engine import (
    DbEngineMapIsEmptyError,
)

from genesis_block_explorer.models.genesis.aux.block import BlockModel
from genesis_block_explorer.models.genesis.aux.block.header import HeaderModel
from genesis_block_explorer.models.genesis.aux.session import (
    AuxSessionManager, 
)

from .blockchain_commons import d1, d3, get_txs
from .test_models_genesis_aux_block import (
    my_setup,
    my_teardown,
    create_tables,
    create_test_app,
    update_aux_db_engine_discovery_map,
)

seq_nums = (1, ) # 2, 3)
involved_models = [BlockModel, HeaderModel]

@with_setup(my_setup, my_teardown)
def test_update_from_dict():
    app = create_test_app()
    new_map = update_aux_db_engine_discovery_map(app, force_update=True,
                                       aux_db_engine_name_prefix='test_aux_')
    sm = AuxSessionManager(app=app)
    sn = 1
    session = sm.get(sn)
    create_tables([BlockModel, HeaderModel], sm.get_engine(sn))
    hd  = get_block_data_from_dict(d3[0])['header']
    len_first = len(HeaderModel.query.with_session(session).all())
    HeaderModel.update_from_dict(hd, session=session)
    assert len(HeaderModel.query.with_session(session).all()) == len_first + 1

@with_setup(my_setup, my_teardown)
def test_update_from_header():
    app = create_test_app()
    new_map = update_aux_db_engine_discovery_map(app, force_update=True,
                                       aux_db_engine_name_prefix='test_aux_')
    sm = AuxSessionManager(app=app)
    sn = 1
    session = sm.get(sn)
    hd = get_block_data_from_dict(d3[0])['header']
    len_first = len(HeaderModel.query.with_session(session).all())
    h = Header(b64decode_hashes=True, from_dict=hd)
    HeaderModel.update_from_header(h, session=session)
    assert len(HeaderModel.query.with_session(session).all()) == len_first + 1

