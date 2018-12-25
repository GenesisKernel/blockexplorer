from sqlalchemy import exc

from genesis_block_explorer.app import create_lean_app
from genesis_block_explorer.db import db
from genesis_block_explorer.models.genesis.aux.config import (
    update_aux_db_engine_discovery_map
)
from genesis_block_explorer.models.genesis.aux.session import (
    AuxSessionManager, 
)

seq_nums = (1, ) 
involved_models = []

def init_db():
    db.create_all()

def create_test_app():
    app = create_lean_app()
    app.app_context().push()
    update_aux_db_engine_discovery_map(app, force_update=True,
                                       aux_db_engine_name_prefix='test_aux_')
    return app

def create_tables(models, engine, recreate_if_exists=True):
    for model in models:
        if recreate_if_exists:
            try:
                model.__table__.drop(engine)
            except (exc.OperationalError, exc.ProgrammingError) as e:
                pass

        try:
            model.__table__.create(engine)
        except (exc.OperationalError, exc.ProgrammingError) as e:
            print("Can'n create table for model %s, error: %s" % (model, e))

def create_tables_by_seq_nums(**kwargs):
    app = kwargs.get('app', create_test_app())
    recreate_if_exists = kwargs.get('recreate_if_exists', True)
    _seq_nums = kwargs.get('seq_nums', seq_nums)
    _involved_models = kwargs.get('involved_models', involved_models)
    for seq_num in _seq_nums:
        asm = AuxSessionManager(app=app)
        print("test.utis create_tables_by_seq_nums 1 engine: %s" % asm.get_engine(seq_num))
        create_tables(_involved_models, asm.get_engine(seq_num),
                      recreate_if_exists=recreate_if_exists)

def common_setup(**kwargs):
    app = kwargs.get('app', create_test_app())
    recreate_if_exists = kwargs.get('recreate_if_exists', True)
    _seq_nums = kwargs.get('seq_nums', seq_nums)
    _involved_models = kwargs.get('involved_models', involved_models)

    aux_prefix = 'test_aux_'
    app = create_test_app()
    db.init_app(app)
    with app.app_context():
        init_db()
    create_tables_by_seq_nums(app=app, seq_nums=_seq_nums,
                              involved_models=_involved_models,
                              recreate_if_exists=recreate_if_exists)

def my_teardown():
    pass
