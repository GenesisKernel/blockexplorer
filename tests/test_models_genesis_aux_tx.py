from nose import with_setup

import datetime 
from sqlalchemy import exc

from genesis_blockchain_api_client.blockchain.block import (
    Block, get_block_id_from_dict, get_block_data_from_dict
)
from genesis_blockchain_api_client.blockchain.tx import Tx
from genesis_blockchain_api_client.blockchain.tx_set import TxSet
from genesis_block_explorer.db import db
from genesis_block_explorer.models.genesis.aux.tx import TxModel
from genesis_block_explorer.models.genesis.aux.session import (
    AuxSessionManager, 
)

from .blockchain_commons import d1, d3, get_txs
from .test_models_genesis_aux_block import (
    init_db,
    create_tables,
    create_test_app,
    my_setup,
    my_teardown,
    update_aux_db_engine_discovery_map,
)

seq_nums = (1, ) # 2, 3)
involved_models = [TxModel]

@with_setup(my_setup, my_teardown)
def test_update_from_dict():
    app = create_test_app()
    new_map = update_aux_db_engine_discovery_map(app, force_update=True,
                                       aux_db_engine_name_prefix='test_aux_')
    sm = AuxSessionManager(app=app)
    sn = 1
    session = sm.get(sn)

    td = get_block_data_from_dict(d3[0])['transactions'][0]
    len_first = len(TxModel.query.with_session(session).all())
    TxModel.update_from_dict(td, session=session)
    assert len(TxModel.query.with_session(session).all()) == len_first + 1

@with_setup(my_setup, my_teardown)
def test_update_from_list_of_dicts():
    app = create_test_app()
    new_map = update_aux_db_engine_discovery_map(app, force_update=True,
                                       aux_db_engine_name_prefix='test_aux_')
    sm = AuxSessionManager(app=app)
    sn = 1
    session = sm.get(sn)

    td = get_block_data_from_dict(d3[1])['transactions']
    len_first = len(TxModel.query.with_session(session).all())
    TxModel.update_from_list_of_dicts(td, session=session)
    assert len(TxModel.query.with_session(session).all()) == len_first + len(td)

@with_setup(my_setup, my_teardown)
def test_update_from_tx():
    app = create_test_app()
    new_map = update_aux_db_engine_discovery_map(app, force_update=True,
                                       aux_db_engine_name_prefix='test_aux_')
    sm = AuxSessionManager(app=app)
    sn = 1
    session = sm.get(sn)

    td = get_block_data_from_dict(d3[0])['transactions'][0]
    len_first = len(TxModel.query.with_session(session).all())
    tx = Tx(b64decode_hashes=True, from_dict=td)
    TxModel.update_from_tx(tx, session=session)
    assert len(TxModel.query.with_session(session).all()) == len_first + 1

@with_setup(my_setup, my_teardown)
def test_update_from_tx_set():
    app = create_test_app()
    new_map = update_aux_db_engine_discovery_map(app, force_update=True,
                                       aux_db_engine_name_prefix='test_aux_')
    sm = AuxSessionManager(app=app)
    sn = 1
    session = sm.get(sn)

    td = get_block_data_from_dict(d3[0])['transactions']
    len_first = len(TxModel.query.with_session(session).all())
    tx = TxSet(b64decode_hashes=True, from_list=td)
    TxModel.update_from_tx_set(tx, session=session)
    assert len(TxModel.query.with_session(session).all()) == len_first + tx.count

