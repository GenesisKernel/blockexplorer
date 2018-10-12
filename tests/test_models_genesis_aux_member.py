from nose import with_setup

from decimal import Decimal 

from flask import Flask, current_app

from sqlalchemy import exc
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm.session import Session

from genesis_block_explorer.db import db

from genesis_block_explorer.models.db_engine.engine import (
    DbEngineMapIsEmptyError,
)

from genesis_block_explorer.models.genesis.aux.config import (
    update_aux_db_engine_discovery_map
)
from genesis_block_explorer.models.genesis.aux.member import MemberModel
from genesis_block_explorer.models.genesis.aux.session import (
    AuxSessionManager, 
)

from genesis_block_explorer.models.genesis.aux.utils import (
    key_id_to_ukey_id
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
involved_models = [MemberModel]
app = create_test_app()
update_aux_db_engine_discovery_map(app, force_update=True,
                                   aux_db_engine_name_prefix='test_aux_')

from genesis_block_explorer.models.db_engine.session import SessionManager
from genesis_block_explorer.models.genesis.explicit import (
    get_ecosystem_model, get_keys_model, 
)

ALLOW_BACKEND_DISTRUCTIVE_TESTS = False
sm = SessionManager(app=app)
EsKeys = get_keys_model(backend_features=sm.get_be_features(1))
Ecosystem = get_ecosystem_model(backend_features=sm.get_be_features(1))

@with_setup(my_setup, my_teardown)
def test_es_keys_model_version():
    seq_num = 1
    col_names = [c.name for c in EsKeys.__table__.columns]

@with_setup(my_setup, my_teardown)
def test_es_keys_query():
    seq_num = 1
    assert EsKeys.query.with_session(sm.get(seq_num)).count() \
            >= len(app.config.get('DB_ENGINE_DISCOVERY_MAP'))

@with_setup(my_setup, my_teardown)
def test_member_object_creation():
    app = create_test_app()
    update_aux_db_engine_discovery_map(app, force_update=True,
                                       aux_db_engine_name_prefix='test_aux_')
    asm = AuxSessionManager(app=app)
    seq_num  = 1
    engine = asm.get_engine(seq_num)
    session = asm.get(seq_num)
    create_tables(involved_models, engine)
    assert session.query(MemberModel).with_session(asm.get(seq_num)).count() == 0

@with_setup(my_setup, my_teardown)
def test_member_add_record_from_dict():
    app = create_test_app()
    update_aux_db_engine_discovery_map(app, force_update=True,
                                       aux_db_engine_name_prefix='test_aux_')
    asm = AuxSessionManager(app=app)
    seq_num  = 1
    engine = asm.get_engine(seq_num)
    session = asm.get(seq_num)
    session.query(MemberModel).delete()
    assert session.query(MemberModel).count() == 0
    d = {
        'ecosystem_id': 1,
        'key_id': -123,
        'ukey_id': '456',
        'pub': 'a9823432',
        'amount': 13.1,
        'maxpay': 10.2,
        'multi': 1,
        'deleted': 1,
        'blocked': 1,
    }
    MemberModel.add_record_from_dict(d, session=session)
    assert session.query(MemberModel).count() == 1
    i = session.query(MemberModel).first()
    for k, v in d.items():
        assert hasattr(i, k)
        val = getattr(i, k)
        if k in ('amount', 'maxpay'):
            assert float(v) == float(val)
        else:
            assert val == v

def assert_eskeys_and_member_instances_eq(eskeys_inst, member_inst):
    d = eskeys_inst.to_dict()
    for k, v in d.items():
        if k == 'pub':
            assert v.hex() == getattr(member_inst, k)
        elif k in ('amount', 'maxpay'):
            assert float(v) == float(getattr(member_inst, k))
        elif k == 'id':
            assert v == member_inst.key_id
            assert key_id_to_ukey_id(v) == member_inst.ukey_id
        else:
            assert v == getattr(member_inst, k)
    assert eskeys_inst.get_ecosystem() == member_inst.ecosystem_id

@with_setup(my_setup, my_teardown)
def test_member_add_record_from_model_instance():
    app = create_test_app()
    update_aux_db_engine_discovery_map(app, force_update=True,
                                       aux_db_engine_name_prefix='test_aux_')
    asm = AuxSessionManager(app=app)
    seq_num  = 1
    engine = asm.get_engine(seq_num)
    session = asm.get(seq_num)
    m_session = sm.get(seq_num)
    session.query(MemberModel).delete()
    assert session.query(MemberModel).count() == 0
    assert m_session.query(EsKeys).count() > 0
    ecosystem_id = 1
    EsKeys.set_ecosystem(ecosystem_id)
    m_instance = m_session.query(EsKeys).first()
    assert isinstance(m_instance, EsKeys)
    MemberModel.add_record_from_model_instance(m_instance, session=session)
    assert session.query(MemberModel).count() == 1
    instance = session.query(MemberModel).first()
    assert_eskeys_and_member_instances_eq(m_instance, instance)

@with_setup(my_setup, my_teardown)
def test_add_all_records_from_model():
    app = create_test_app()
    update_aux_db_engine_discovery_map(app, force_update=True,
                                       aux_db_engine_name_prefix='test_aux_')
    asm = AuxSessionManager(app=app)
    seq_num  = 1
    engine = asm.get_engine(seq_num)
    session = asm.get(seq_num)
    m_session = sm.get(seq_num)
    session.query(MemberModel).delete()
    assert session.query(MemberModel).count() == 0
    assert m_session.query(EsKeys).count() > 0
    ecosystem_id = 1
    EsKeys.set_ecosystem(ecosystem_id)
    MemberModel.add_all_records_from_model(EsKeys,
                                           session=session,
                                           model_session=m_session)
    assert session.query(MemberModel).count() == m_session.query(EsKeys).count()
    for m_item in m_session.query(EsKeys).all():
        item = session.query(MemberModel).filter_by(key_id=m_item.id).one()
        assert_eskeys_and_member_instances_eq(m_item, item)


@with_setup(my_setup, my_teardown)
def test_add_all_records_for_all_ecosystems():
    app = create_test_app()
    update_aux_db_engine_discovery_map(app, force_update=True,
                                       aux_db_engine_name_prefix='test_aux_')
    asm = AuxSessionManager(app=app)
    seq_num  = 1
    engine = asm.get_engine(seq_num)
    session = asm.get(seq_num)
    m_session = sm.get(seq_num)
    session.query(MemberModel).delete()
    assert session.query(MemberModel).count() == 0
    assert m_session.query(EsKeys).count() > 0
    MemberModel.add_all_records_for_all_ecosystems(EsKeys,
                                           ecosystem_model=Ecosystem,
                                           session=session,
                                           model_session=m_session)
    total = 0
    for es in m_session.query(Ecosystem).all():
        EsKeys.set_ecosystem(es.id)
        for m_item in m_session.query(EsKeys).all():
            item = session.query(MemberModel).filter_by(key_id=m_item.id).one()
            assert_eskeys_and_member_instances_eq(m_item, item)
        total += m_session.query(EsKeys).count()
    assert session.query(MemberModel).count() == total

@with_setup(my_setup, my_teardown)
def test_compare_num_of_all_records_for_all_ecosystems():
    app = create_test_app()
    update_aux_db_engine_discovery_map(app, force_update=True,
                                       aux_db_engine_name_prefix='test_aux_')
    asm = AuxSessionManager(app=app)
    seq_num  = 1
    engine = asm.get_engine(seq_num)
    session = asm.get(seq_num)
    m_session = sm.get(seq_num)
    session.query(MemberModel).delete()
    assert session.query(MemberModel).count() == 0
    assert m_session.query(EsKeys).count() > 0
    MemberModel.add_all_records_for_all_ecosystems(EsKeys,
                                           ecosystem_model=Ecosystem,
                                           session=session,
                                           model_session=m_session)

    l = session.query(MemberModel).count() 
    assert l > 0
    MemberModel.compare_num_of_all_records_for_all_ecosystems(EsKeys,
                                           ecosystem_model=Ecosystem,
                                           session=session,
                                           model_session=m_session)
    session.delete(session.query(MemberModel).first())
    session.commit()
    l2 = session.query(MemberModel).count() 
    assert l > l2
    compare_num_error_caught = False
    try:
        MemberModel.compare_num_of_all_records_for_all_ecosystems(EsKeys,
                                           ecosystem_model=Ecosystem,
                                           session=session,
                                           model_session=m_session)
    except MemberModel.CompareNumError:
        compare_num_error_caught = True
    assert compare_num_error_caught

@with_setup(my_setup, my_teardown)
def nontest_update_all_records_for_all_ecosystems():
    app = create_test_app()
    update_aux_db_engine_discovery_map(app, force_update=True,
                                       aux_db_engine_name_prefix='test_aux_')
    asm = AuxSessionManager(app=app)
    seq_num  = 1
    engine = asm.get_engine(seq_num)
    session = asm.get(seq_num)
    m_session = sm.get(seq_num)
    session.query(MemberModel).delete()
    assert session.query(MemberModel).count() == 0
    assert m_session.query(EsKeys).count() > 0
    MemberModel.add_all_records_for_all_ecosystems(EsKeys,
                                           ecosystem_model=Ecosystem,
                                           session=session,
                                           model_session=m_session)
    total = 0
    for es in m_session.query(Ecosystem).all():
        EsKeys.set_ecosystem(es.id)
        total += m_session.query(EsKeys).count()
    assert session.query(MemberModel).count() == total

    MemberModel.compare_num_of_all_records_for_all_ecosystems(EsKeys,
                                           ecosystem_model=Ecosystem,
                                           session=session,
                                           model_session=m_session)

    l = session.query(MemberModel).count() 
    assert l > 0
    session.delete(session.query(MemberModel).first())
    l2 = session.query(MemberModel).count() 
    assert l2 == l - 1
    MemberModel.update_all_records_for_all_ecosystems(EsKeys,
                                           ecosystem_model=Ecosystem,
                                           session=session,
                                           model_session=m_session)
    l3 = session.query(MemberModel).count() 
    assert l3 == l

    m_l = m_session.query(EsKeys).count()
    assert l3  == m_l
    if ALLOW_BACKEND_DISTRUCTIVE_TESTS:
        m_item = m_session.query(EsKeys).first()
        m_data = m_item.to_dict()
        m_item_new = EsKeys(**m_data)
        m_session.delete(m_item)
        m_session.commit()
        m_l2 = m_session.query(EsKeys).count()

        MemberModel.update_all_records_for_all_ecosystems(EsKeys,
                                                   ecosystem_model=Ecosystem,
                                                   session=session,
                                                   model_session=m_session)
        l4 = session.query(MemberModel).count() 
        assert l4 == m_l2

        m_session.add(m_item_new)
        m_session.commit()

        m_l3 = m_session.query(EsKeys).count()
        assert m_l == m_l3


