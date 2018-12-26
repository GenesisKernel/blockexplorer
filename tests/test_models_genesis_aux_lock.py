from nose import with_setup

import os
import time
from datetime import timedelta, datetime
from sqlalchemy import exc

from genesis_block_explorer.db import db
from genesis_block_explorer.models.genesis.aux.config import (
    update_aux_db_engine_discovery_map
)
from genesis_block_explorer.models.genesis.aux.lock import (
    LockModel
)
from genesis_block_explorer.models.db_engine.engine import (
    DbEngineMapIsEmptyError
)
from genesis_block_explorer.models.genesis.aux.session import (
    AuxSessionManager, 
)
from genesis_block_explorer.process import check_pid, get_fake_pid

def my_setup():
    create_test_app()

def my_teardown():
    pass

def create_test_app():
    from genesis_block_explorer.app import create_app, create_lean_app
    app = create_lean_app()
    app.app_context().push()
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

@with_setup(my_setup, my_teardown)
def test_is_locked():
    app = create_test_app()
    new_map = update_aux_db_engine_discovery_map(app, force_update=True,
                                          aux_db_engine_name_prefix='test_aux_')
    sm = AuxSessionManager(app=app)
    seq_num = 1
    session = sm.get(seq_num)
    create_tables([LockModel], sm.get_engine(seq_num))

    # default context
    assert len(LockModel.query.with_session(session=session).all()) == 0
    assert LockModel.is_locked(session=session) == False
    l = LockModel()
    session.add(l)
    session.commit()
    assert len(LockModel.query.with_session(session=session).all()) == 1
    l = LockModel()
    session.add(l)
    session.commit()
    assert len(LockModel.query.with_session(session=session).all()) == 2
    assert LockModel.is_locked(session=session) == True

    # filler context
    assert len(LockModel.query.with_session(session=session).filter_by(context='filler').all()) == 0
    assert LockModel.is_locked(session=session, context='filler') == False
    l = LockModel(context='filler')
    session.add(l)
    session.commit()
    assert len(LockModel.query.with_session(session=session).filter_by(context='filler').all()) == 1
    assert LockModel.is_locked(session=session, context='filler') == True
    l = LockModel(context='filler')
    session.add(l)
    session.commit()
    assert len(LockModel.query.with_session(session=session).filter_by(context='filler').all()) == 2
    assert LockModel.is_locked(session=session, context='filler') == True

@with_setup(my_setup, my_teardown)
def test_lock():
    app = create_test_app()
    new_map = update_aux_db_engine_discovery_map(app, force_update=True,
                                          aux_db_engine_name_prefix='test_aux_')
    sm = AuxSessionManager(app=app)
    seq_num = 1
    session = sm.get(seq_num)
    create_tables([LockModel], sm.get_engine(seq_num))

    assert LockModel.is_locked(session=session) == False
    LockModel.lock(session=session)
    assert LockModel.is_locked(session=session) == True
    LockModel.lock(session=session)
    assert LockModel.is_locked(session=session) == True
    
    assert LockModel.is_locked(session=session, context='filler') == False
    LockModel.lock(session=session, context='filler')
    assert LockModel.is_locked(session=session, context='filler') == True
    LockModel.lock(session=session, context='filler')
    assert LockModel.is_locked(session=session, context='filler') == True

@with_setup(my_setup, my_teardown)
def test_unlock():
    app = create_test_app()
    new_map = update_aux_db_engine_discovery_map(app, force_update=True,
                                          aux_db_engine_name_prefix='test_aux_')
    sm = AuxSessionManager(app=app)
    seq_num = 1
    session = sm.get(seq_num)
    create_tables([LockModel], sm.get_engine(seq_num))

    assert LockModel.is_locked(session=session) == False
    LockModel.lock(session=session)
    assert LockModel.is_locked(session=session) == True
    LockModel.unlock(session=session)
    assert LockModel.is_locked(session=session) == False
    
    assert LockModel.is_locked(session=session, context='filler') == False
    LockModel.lock(session=session, context='filler')
    assert LockModel.is_locked(session=session, context='filler') == True
    LockModel.unlock(session=session, context='filler')
    assert LockModel.is_locked(session=session, context='filler') == False

@with_setup(my_setup, my_teardown)
def test_get_latest_lock():
    app = create_test_app()
    new_map = update_aux_db_engine_discovery_map(app, force_update=True,
                                          aux_db_engine_name_prefix='test_aux_')
    sm = AuxSessionManager(app=app)
    seq_num = 1
    session = sm.get(seq_num)
    create_tables([LockModel], sm.get_engine(seq_num))

    assert LockModel.is_locked(session=session) == False
    LockModel.lock(session=session)
    assert LockModel.is_locked(session=session) == True
    q = LockModel.get_latest_lock(session=session)
    assert isinstance(q, LockModel)
    LockModel.unlock(session=session)
    q = LockModel.get_latest_lock(session=session)
    assert q is None 

@with_setup(my_setup, my_teardown)
def test_get_zombie_locks():
    app = create_test_app()
    new_map = update_aux_db_engine_discovery_map(app, force_update=True,
                                          aux_db_engine_name_prefix='test_aux_')
    sm = AuxSessionManager(app=app)
    seq_num = 1
    session = sm.get(seq_num)
    create_tables([LockModel], sm.get_engine(seq_num))

    assert LockModel.is_locked(session=session) == False

    LockModel.lock(session=session)
    assert LockModel.is_locked(session=session) == True
    q = LockModel.get_latest_lock(session=session)
    assert isinstance(q, LockModel)
    assert session.query(LockModel).count() == 1
    LockModel.unlock(session=session)
    assert session.query(LockModel).count() == 0

    LockModel.lock(session=session)
    assert LockModel.is_locked(session=session) == True
    q = LockModel.get_latest_lock(session=session)
    assert isinstance(q, LockModel)
    assert session.query(LockModel).count() == 1
    LockModel.lock(session=session)
    assert session.query(LockModel).count() == 2
    LockModel.unlock(session=session)
    assert session.query(LockModel).count() == 0

    #n = os.fork()
    #LockModel.lock(session=session)
    #assert LockModel.is_locked(session=session) == True
    #q = LockModel.get_latest_lock(session=session)
    #print("q: %s" % q)
    #print("is instance: %s" % isinstance(q, LockModel))
    #assert isinstance(q, LockModel)
    #if n > 0: 
    #    print("Parent process and id is : ", os.getpid())
    #else:
    #    print("Child process and id is : ", os.getpid())
    #    return
    #    os._exit(0)
    #time.sleep(1)
    #assert session.query(LockModel).count() == 2
    #LockModel.unlock(session=session)
    #assert session.query(LockModel).count() == 0

    fake_pid = get_fake_pid()
    LockModel.lock(session=session)
    LockModel.lock(session=session, process_id=fake_pid)
    assert LockModel.is_locked(session=session) == True
    assert session.query(LockModel).count() == 2
    qs = session.query(LockModel).all()
    qs_pids = [q.process_id for q in qs]

    assert fake_pid in qs_pids
    q = LockModel.get_latest_lock(session=session)
    assert isinstance(q, LockModel)
    assert session.query(LockModel).count() == 2

    zqs = LockModel.get_zombie_locks(session=session)
    zqs_pids = [q.process_id for q in zqs]
    assert len(zqs_pids) == 1
    assert fake_pid in zqs_pids

    LockModel.unlock(session=session)
    assert session.query(LockModel).count() == 0

def test_delete_zombie_locks():
    app = create_test_app()
    new_map = update_aux_db_engine_discovery_map(app, force_update=True,
                                          aux_db_engine_name_prefix='test_aux_')
    sm = AuxSessionManager(app=app)
    seq_num = 1
    session = sm.get(seq_num)
    create_tables([LockModel], sm.get_engine(seq_num))

    assert LockModel.is_locked(session=session) == False

    fake_pid = get_fake_pid()
    LockModel.lock(session=session)
    LockModel.lock(session=session, process_id=fake_pid)
    assert LockModel.is_locked(session=session) == True
    assert session.query(LockModel).count() == 2
    qs = session.query(LockModel).all()
    qs_pids = [q.process_id for q in qs]

    assert fake_pid in qs_pids
    q = LockModel.get_latest_lock(session=session)
    assert isinstance(q, LockModel)
    assert session.query(LockModel).count() == 2

    zqs = LockModel.get_zombie_locks(session=session)
    zqs_pids = [q.process_id for q in zqs]
    assert len(zqs_pids) == 1
    assert fake_pid in zqs_pids

    LockModel.delete_zombie_locks(session=session)
    zqs = LockModel.get_zombie_locks(session=session)
    zqs_pids = [q.process_id for q in zqs]
    assert len(zqs_pids) == 0

    LockModel.unlock(session=session)
    assert session.query(LockModel).count() == 0

def test_get_expired_locks():
    app = create_test_app()
    new_map = update_aux_db_engine_discovery_map(app, force_update=True,
                                          aux_db_engine_name_prefix='test_aux_')
    sm = AuxSessionManager(app=app)
    seq_num = 1
    session = sm.get(seq_num)
    create_tables([LockModel], sm.get_engine(seq_num))

    assert LockModel.is_locked(session=session) == False

    to = 1

    eqs = LockModel.get_expired_locks(session=session, timeout_secs=to)
    assert len(eqs) == 0
    LockModel.lock(session=session)
    assert LockModel.is_locked(session=session) == True
    lock = LockModel.get_latest_lock(session=session)
    eqs = LockModel.get_expired_locks(session=session, timeout_secs=to)
    assert len(eqs) == 0
    print("Pausing for %d seconds ..." % (to + 1))
    time.sleep(to + 1)
    eqs = LockModel.get_expired_locks(session=session, timeout_secs=to)
    assert len(eqs) == 1

def test_delete_expired_locks():
    app = create_test_app()
    new_map = update_aux_db_engine_discovery_map(app, force_update=True,
                                          aux_db_engine_name_prefix='test_aux_')
    sm = AuxSessionManager(app=app)
    seq_num = 1
    session = sm.get(seq_num)
    create_tables([LockModel], sm.get_engine(seq_num))

    assert LockModel.is_locked(session=session) == False

    to = 1

    eqs = LockModel.get_expired_locks(session=session, timeout_secs=to)
    assert len(eqs) == 0
    LockModel.lock(session=session)
    assert LockModel.is_locked(session=session) == True
    assert session.query(LockModel).count() == 1
    lock = LockModel.get_latest_lock(session=session)
    eqs = LockModel.get_expired_locks(session=session, timeout_secs=to)
    assert len(eqs) == 0
    print("Pausing for %d seconds ..." % (to + 1))
    time.sleep(to + 1)
    LockModel.lock(session=session)
    assert session.query(LockModel).count() == 2
    eqs = LockModel.get_expired_locks(session=session, timeout_secs=to)
    assert len(eqs) == 1
    LockModel.delete_expired_locks(session=session, timeout_secs=to)
    eqs = LockModel.get_expired_locks(session=session, timeout_secs=to)
    assert len(eqs) == 0
    assert session.query(LockModel).count() == 1

def test_clear_garbage():
    app = create_test_app()
    new_map = update_aux_db_engine_discovery_map(app, force_update=True,
                                          aux_db_engine_name_prefix='test_aux_')
    sm = AuxSessionManager(app=app)
    seq_num = 1
    session = sm.get(seq_num)
    create_tables([LockModel], sm.get_engine(seq_num))

    assert LockModel.is_locked(session=session) == False

    to = 1
    fake_pid = get_fake_pid()
    LockModel.lock(session=session)
    time.sleep(to + 1)
    LockModel.lock(session=session)
    LockModel.lock(session=session, process_id=fake_pid)
    assert LockModel.is_locked(session=session) == True
    assert session.query(LockModel).count() == 3
    qs = session.query(LockModel).all()
    qs_pids = [q.process_id for q in qs]

    assert fake_pid in qs_pids
    q = LockModel.get_latest_lock(session=session)
    assert isinstance(q, LockModel)
    assert session.query(LockModel).count() == 3

    zqs = LockModel.get_zombie_locks(session=session)
    zqs_pids = [q.process_id for q in zqs]
    assert len(zqs_pids) == 1
    assert fake_pid in zqs_pids

    eqs = LockModel.get_expired_locks(session=session, timeout_secs=to)
    assert len(eqs) == 1

    LockModel.clear_garbage(session=session, timeout_secs=to)
    zqs = LockModel.get_zombie_locks(session=session)
    zqs_pids = [q.process_id for q in zqs]
    assert len(zqs_pids) == 0

    eqs = LockModel.get_expired_locks(session=session, timeout_secs=to)
    assert len(eqs) == 0

    LockModel.unlock(session=session)
    assert session.query(LockModel).count() == 0
    # TODO: add expired locks case
