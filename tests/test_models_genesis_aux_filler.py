from nose import with_setup

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
from genesis_block_explorer.models.genesis.aux.filler import (
    Filler, FillerIsLockedError,
)
from genesis_block_explorer.models.genesis.aux.session import (
    AuxSessionManager, 
)

from .test_models_genesis_aux_block import (
    init_db,
    create_test_app,
    my_setup,
    my_teardown,
)

seq_nums = (1, ) # 2, 3)
involved_models = []

class TestFiller(Filler):
    def __init__(self, **kwargs):
        kwargs['involved_models'] = []
        super(TestFiller, self).__init__(**kwargs)
        self.context = 'test_filler'

@with_setup(my_setup, my_teardown)
def test_check_dbs():
    app = create_test_app()
    new_map = update_aux_db_engine_discovery_map(app, force_update=True,
                                       aux_db_engine_name_prefix='test_aux_')
    f = Filler(app=app)
    f.check_dbs()

@with_setup(my_setup, my_teardown)
def test_do_if_locked():
    app = create_test_app()
    new_map = update_aux_db_engine_discovery_map(app, force_update=True,
                                       aux_db_engine_name_prefix='test_aux_')
    f = Filler(app=app)
    f.do_if_locked()
    f.lock()
    FillerIsLockedError
    filler_is_locked_error_caught = False
    try:
        f.do_if_locked()
    except FillerIsLockedError as e:
        #print("Exception caught: %s" % e)
        filler_is_locked_error_caught = True
    assert filler_is_locked_error_caught
    f.unlock()
    f.do_if_locked()

@with_setup(my_setup, my_teardown)
def test_multi_context_locking():
    app = create_test_app()
    new_map = update_aux_db_engine_discovery_map(app, force_update=True,
                                       aux_db_engine_name_prefix='test_aux_')
    f = Filler(app=app)
    f.unlock()

    tf = TestFiller(app=app)
    tf.unlock()
    assert not f.is_locked
    assert not tf.is_locked

    #f.lock()
    #assert f.is_locked
    #assert not tf.is_locked
    #f.do_if_locked()
    #f.lock()
    #FillerIsLockedError
    #filler_is_locked_error_caught = False
    #try:
    #    f.do_if_locked()
    #except FillerIsLockedError as e:
    #    #print("Exception caught: %s" % e)
    #    filler_is_locked_error_caught = True
    #assert filler_is_locked_error_caught
    #f.unlock()
    #f.do_if_locked()

