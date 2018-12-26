from nose import with_setup

from genesis_block_explorer.models.genesis.aux.session import (
    AuxSessionManager, 
)

from genesis_block_explorer.models.genesis.aux.member import MemberModel
from genesis_block_explorer.models.genesis.aux.filler import FillerIsLockedError
from genesis_block_explorer.models.genesis.aux.member.filler import MemberFiller

from .test_models_genesis_aux_block import (
    my_setup,
    my_teardown,
    create_tables,
    create_test_app,
    update_aux_db_engine_discovery_map,
)

seq_nums = (1, ) # 2, 3)
involved_models = []

@with_setup(my_setup, my_teardown)
def test_add():
    app = create_test_app()
    new_map = update_aux_db_engine_discovery_map(app, force_update=True,
                                       aux_db_engine_name_prefix='test_aux_')
    sm = AuxSessionManager(app=app)
    seq_num = 1
    session = sm.get(seq_num)
    #assert session.query(MemberModel).count() == 0
    #f = MemberFiller(app=app, seq_num=seq_num, recreate_tables_if_exist=True)
    #f.add()
    #assert session.query(MemberModel).count() > 0

