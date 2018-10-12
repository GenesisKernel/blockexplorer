from nose import with_setup

from sqlalchemy import exc

from genesis_block_explorer.db import db
from genesis_block_explorer.models.genesis.aux.config import (
    update_aux_db_engine_discovery_map
)
from genesis_block_explorer.models.genesis.aux.log import (
    LogModel,
)
from genesis_block_explorer.models.db_engine.engine import (
    DbEngineMapIsEmptyError
)
from genesis_block_explorer.models.genesis.aux.session import (
    AuxSessionManager, 
)

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
def test_add():
    app = create_test_app()
    new_map = update_aux_db_engine_discovery_map(app, force_update=True,
                                          aux_db_engine_name_prefix='test_aux_')
    sm = AuxSessionManager(app=app)
    seq_num = 1
    session = sm.get(seq_num)
    create_tables([LogModel], sm.get_engine(seq_num))

    assert len(LogModel.query.with_session(session=session).all()) == 0
    LogModel.add(session=session, context='filler',
                 caller='fill_block')
    assert len(LogModel.query.with_session(session=session).all()) == 1
    LogModel.add(session=session, context='filler', caller='fill_block')
    assert len(LogModel.query.with_session(session=session).all()) == 2

@with_setup(my_setup, my_teardown)
def test_clear():
    app = create_test_app()
    new_map = update_aux_db_engine_discovery_map(app, force_update=True,
                                          aux_db_engine_name_prefix='test_aux_')
    sm = AuxSessionManager(app=app)
    seq_num = 1
    session = sm.get(seq_num)
    create_tables([LogModel], sm.get_engine(seq_num))

    assert len(LogModel.query.with_session(session=session).all()) == 0
    LogModel.add(session=session, context='filler', caller='fill_block')
    assert len(LogModel.query.with_session(session=session).all()) == 1
    LogModel.add(session=session, context='filler', caller='fill_block')
    assert len(LogModel.query.with_session(session=session).all()) == 2
    LogModel.clear(session=session)
    assert len(LogModel.query.with_session(session=session).all()) == 0

