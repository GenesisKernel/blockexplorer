from nose import with_setup

from sqlalchemy.engine.base import Engine

from flask import Flask, current_app

from genesis_block_explorer.app import create_lean_app as create_app

def create_test_app():
    from genesis_block_explorer.app import create_lean_app as create_app
    app = create_app()
    app.app_context().push()
    return app

app = create_test_app()

from genesis_block_explorer.models.db_engine.seq_num import (
    get_valid_seq_num, WrongDbSeqNumError
)

def my_setup():
    pass

def my_teardown():
    pass

@with_setup(my_setup, my_teardown)
def test_get_valid_seq_num():
    if len(app.config.get('DB_ENGINE_DISCOVERY_MAP')) > 0:
        over = len(app.config.get('DB_ENGINE_DISCOVERY_MAP')) + 1
        wrong_db_seq_num_error_caugth = False
        try:
            seq_num = get_valid_seq_num(app, over)
        except WrongDbSeqNumError:
            wrong_db_seq_num_error_caugth = True
        assert wrong_db_seq_num_error_caugth


