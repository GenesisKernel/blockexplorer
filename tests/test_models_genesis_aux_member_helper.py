from nose import with_setup

from flask import Flask, current_app

from sqlalchemy.sql.schema import MetaData
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy import exc
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm.session import Session

from genesis_block_explorer.db import db

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
from genesis_block_explorer.models.genesis.aux.member import MemberModel
from genesis_block_explorer.models.genesis.aux.member.helper import (
    MemberHelperModel, MemberHelperManager,
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
involved_models = [MemberModel]
involved_helpers_models = [MemberHelperModel]

def my_setup():
    aux_prefix = 'test_aux_'
    app = create_test_app()
    update_aux_db_engine_discovery_map(app, force_update=True,
                                       aux_db_engine_name_prefix='test_aux_')
    db.init_app(app)
    with app.app_context():
        init_db()
    create_tables_by_seq_nums(app=app)
    engine = get_aux_helpers_engine(app)
    create_tables(involved_helpers_models, engine, recreate_if_exists=True)

@with_setup(my_setup, my_teardown)
def test_member_helper_manager():
    #app = create_test_app()
    mhm = MemberHelperManager(engine_echo=False)
    assert len(mhm.session.query(mhm.model).all()) == 0
    mhm.session.add(mhm.model(name='Name1', value='Value1'))
    mhm.session.add(mhm.model(name='Name2', value='Value2'))
    mhm.session.commit()
    assert len(mhm.session.query(mhm.model).all()) == 2
    mhm.session.query(mhm.model).delete()
    assert len(mhm.session.query(mhm.model).all()) == 0
    del(mhm)

@with_setup(my_setup, my_teardown)
def test_update_from_main_model_instance_via_manager():
    app = create_test_app()
    mhm = MemberHelperManager(app=app, engine_echo=True)

    sm = AuxSessionManager(app=app)
    seq_num = 1
    mm_session = sm.get(seq_num)
    mm_engine = sm.get_engine(seq_num)
    create_tables([MemberModel], mm_engine, recreate_if_exists=True)

    len_mm_first = len(MemberModel.query.with_session(mm_session).all())
    assert len_mm_first == 0
    d = {
        'ecosystem_id': 1,
        'key_id': -123,
        'wallet': '456',
        'pub': 'a9823432',
        'amount': 13.1,
        'maxpay': 10.2,
        'multi': 1,
        'deleted': 1,
        'blocked': 1,
    }
    MemberModel.add_record_from_dict(d, session=mm_session)
    assert len(MemberModel.query.with_session(mm_session).all()) == len_mm_first + 1

    mm_instance = MemberModel.query.with_session(mm_session).all()[0]

    len_first = len(mhm.session.query(mhm.model).all())
    assert len_first == 0
    mhm.model.update_from_main_model_instance(mm_instance, session=mhm.session, main_model_session=mm_session, seq_num=seq_num, ecosystem_id=1)
    num_of_mhm_records = len(MemberModel.__table__.columns) - len(MemberHelperModel.get_drop_fields())
    assert len(mhm.session.query(mhm.model).all()) == len_first + num_of_mhm_records

    print("---------------ALL: %s" % mhm.session.query(mhm.model).filter_by(seq_num=seq_num, id=mm_instance.id).all())
    mhm.session.query(mhm.model).filter_by(seq_num=seq_num, id=mm_instance.id).delete()
    mhm.model.update_from_main_model_instance(mm_instance, session=mhm.session, main_model_session=mm_session, seq_num=seq_num, ecosystem_id=1)
    print("len of mhm: %s" % len(mhm.session.query(mhm.model).all()))
    #assert len(mhm.session.query(mhm.model).all()) == len_first + num_of_mhm_records

