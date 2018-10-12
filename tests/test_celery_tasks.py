

from nose import with_setup

from flask import Flask, current_app

from sqlalchemy import exc
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm.session import Session

from genesis_block_explorer.celery.tasks import (
    block_filler_update, block_filler_update_task,
    run_block_fillers_updates, run_async_block_fillers_updates,
)
from genesis_block_explorer.models.genesis.aux.config import (
    update_aux_db_engine_discovery_map
)

def create_test_app():
    from genesis_block_explorer.app import create_lean_app as create_app
    app = create_app()
    app.app_context().push()
    #update_aux_db_engine_discovery_map(app, force_update=True,
    #                                   aux_db_engine_name_prefix='test_aux_')
    return app

def my_setup():
    app = create_test_app()

def my_teardown():
    pass

@with_setup(my_setup, my_teardown)
def nontest_run_block_fillers_updates():
    app = create_test_app()
    print("disc map: %s" % app.config.get('DB_ENGINE_DISCOVERY_MAP'))
    print("aux map: %s" % app.config.get('AUX_DB_ENGINE_DISCOVERY_MAP'))
    print("api urls: %s" % app.config.get('BACKEND_API_URLS'))

@with_setup(my_setup, my_teardown)
def test_block_filler_update():
    seq_num = 1
    block_filler_update(seq_num)

@with_setup(my_setup, my_teardown)
def test_run_block_fillers_updates():
    results = run_block_fillers_updates()
    print("results: %s" % results)

@with_setup(my_setup, my_teardown)
def nontest_run_async_block_fillers_updates():
    async_results = run_async_block_fillers_updates()
    for async_result in async_results:
        task_id = async_result.task_id
        res = block_filler_update_task.AsyncResult(task_id).get(timeout=20.0)
        print("async_result: %s task_id: %s type(task_id): %s" % (async_result, task_id, type(async_result)))
        #res = block_filler_update_task.AsyncResult(task_id).get()
        print("res: %s" % res)
