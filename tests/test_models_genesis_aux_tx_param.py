from nose import with_setup

from sqlalchemy import exc

from genesis_blockchain_api_client.blockchain.block import (
    Block, get_block_id_from_dict, get_block_data_from_dict
)
from genesis_blockchain_api_client.blockchain.tx import Tx
from genesis_blockchain_api_client.blockchain.tx.param import Param
from genesis_blockchain_api_client.blockchain.tx.param_set import ParamSet
from genesis_block_explorer.db import db
from genesis_block_explorer.models.genesis.aux.tx import TxModel
from genesis_block_explorer.models.genesis.aux.tx.param import ParamModel
from genesis_block_explorer.models.genesis.aux.session import (
    AuxSessionManager, 
)

from .blockchain_commons import d1, d3, get_txs
from .test_models_genesis_aux_block import (
    init_db,
    create_test_app,
    create_tables,
    my_setup,
    my_teardown,
    update_aux_db_engine_discovery_map,
)

seq_nums = (1, ) # 2, 3)
involved_models = [TxModel, ParamModel]

@with_setup(my_setup, my_teardown)
def nontest_aux_session_manager():
    app = create_test_app()
    new_map = update_aux_db_engine_discovery_map(app, force_update=True,
                                       aux_db_engine_name_prefix='test_aux_')
    sm = AuxSessionManager(app=app)
    sn = 1
    session = sm.get(sn)

@with_setup(my_setup, my_teardown)
def test_update_from_param():
    app = create_test_app()
    new_map = update_aux_db_engine_discovery_map(app, force_update=True,
                                       aux_db_engine_name_prefix='test_aux_')
    sm = AuxSessionManager(app=app)
    sn = 1
    session = sm.get(sn)
    create_tables([TxModel, ParamModel], sm.get_engine(sn))
    
    # TODO: fix when:
    # td = get_block_data_from_dict(d3[0])['transactions'][0]['params'] # [0]
    td = get_block_data_from_dict(d3[0])['transactions'][1]['params'] # [0]
    print("test_update_from_param 2 td: %s" % td)
    p0n = tuple(td.keys())[0]
    p0v = td[p0n]
    pd = {p0n: p0v}
    app = create_test_app()
    assert len(ParamModel.query.with_session(session).all()) == 0
    p = Param(**pd)
    ParamModel.update_from_param(p, session=session)
    assert len(ParamModel.query.with_session(session).all()) == 1
    pm = ParamModel.query.with_session(session).all()[0]
    assert pm.name == p0n
    assert pm.value == p0v
    try:
        ParamModel.update_from_param(p, session=session)
    except exc.IntegrityError:
        pass

@with_setup(my_setup, my_teardown)
def nontest_update_from_param_set():
    app = create_test_app()
    new_map = update_aux_db_engine_discovery_map(app, force_update=True,
                                       aux_db_engine_name_prefix='test_aux_')
    sm = AuxSessionManager(app=app)
    sn = 1
    session = sm.get(sn)
    create_tables([TxModel, ParamModel], sm.get_engine(sn))

    pd = get_block_data_from_dict(d3[0])['transactions'][0]['params']
    assert len(ParamModel.query.with_session(session).all()) == 0
    ps = ParamSet(**pd)
    ParamModel.update_from_param_set(ps, session=session)
    assert len(ParamModel.query.with_session(session).all()) == len(pd)
    pm = ParamModel.query.with_session(session).all()[0]
    try:
        ParamModel.update_from_param_set(ps, session=session)
    except exc.IntegrityError:
        pass
