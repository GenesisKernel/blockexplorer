from nose import with_setup

from sqlalchemy import exc

from genesis_block_explorer.models.genesis.aux.session import (
    AuxSessionManager, 
)

from genesis_block_explorer.models.genesis.aux.block.error import ErrorModel

from .utils import common_setup, create_test_app, my_teardown

seq_nums = (1, ) # 2, 3)
involved_models = [ErrorModel]

def my_setup():
    common_setup(seq_nums=seq_nums, involved_models=involved_models)

@with_setup(my_setup, my_teardown)
def test_create_obj():
    app = create_test_app()
    sm = AuxSessionManager(app=app)
    seq_num = 1
    session = sm.get(seq_num)
    assert session.query(ErrorModel).count() == 0
    e = ErrorModel(block_id=111, error="This is error", raw_error="Raw error")
    session.add(e)
    session.commit()
    assert session.query(ErrorModel).count() == 1

