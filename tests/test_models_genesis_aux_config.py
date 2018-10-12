from nose import with_setup

from genesis_block_explorer.models.genesis.aux.config import (
    update_aux_db_engine_discovery_map, get_num_of_backends,
    update_aux_helpers_bind_name,
)

def create_test_app():
    from genesis_block_explorer.app import create_lean_app as create_app
    app = create_app()
    app.app_context().push()
    return app

def my_setup():
    pass

def my_teardown():
    pass

@with_setup(my_setup, my_teardown)
def test_update_aux_db_engine_discovery_map():
    app = create_test_app()
    app.config['AUX_DB_ENGINE_DISCOVERY_MAP'] = {'test_bind_name1': 'some'}
    src_config = app.config.get('AUX_DB_ENGINE_DISCOVERY_MAP').copy()
    new_aux_map = update_aux_db_engine_discovery_map(app)
    assert src_config == app.config.get('AUX_DB_ENGINE_DISCOVERY_MAP')
    new_aux_map = update_aux_db_engine_discovery_map(app, force_update=True)
    assert src_config != app.config.get('AUX_DB_ENGINE_DISCOVERY_MAP')
    for name, value in app.config.get('DB_ENGINE_DISCOVERY_MAP').items():
        assert 'aux_' + name in app.config.get('AUX_DB_ENGINE_DISCOVERY_MAP')
        assert app.config.get('AUX_DB_ENGINE_DISCOVERY_MAP')['aux_' + name] == value
    new_aux_map = update_aux_db_engine_discovery_map(app, force_update=True,
                                      aux_db_engine_name_prefix='test_aux_')
    assert src_config != app.config.get('AUX_DB_ENGINE_DISCOVERY_MAP')
    for name, value in app.config.get('DB_ENGINE_DISCOVERY_MAP').items():
        assert 'test_aux_' + name in app.config.get('AUX_DB_ENGINE_DISCOVERY_MAP')
        assert app.config.get('AUX_DB_ENGINE_DISCOVERY_MAP')['test_aux_' + name] == value

@with_setup(my_setup, my_teardown)
def test_update_aux_helpers_bind_name():
    app = create_test_app()
    app.config['AUX_HELPERS_BIND_NAME'] = 'this_is_a_test'
    src_name = app.config.get('AUX_HELPERS_BIND_NAME')
    update_aux_helpers_bind_name(app)
    assert app.config.get('AUX_HELPERS_BIND_NAME') == src_name
    update_aux_helpers_bind_name(app, prefix='some_')
    assert app.config.get('AUX_HELPERS_BIND_NAME') == 'some_' + src_name

@with_setup(my_setup, my_teardown)
def test_get_num_of_backends():
    app = create_test_app()
    num = get_num_of_backends(app)
    app.config['DB_ENGINE_DISCOVERY_MAP'] = {'test_bind_name1': 'name1'}
    app.config['AUX_DB_ENGINE_DISCOVERY_MAP'] = {'test_bind_name1': 'name1'}
    app.config['BACKEND_API_URLS'] = {1: 'test_url1', 2: 'test_url2'}
    assert get_num_of_backends(app) == 1

    app.config['DB_ENGINE_DISCOVERY_MAP'] = {'test_bind_name1': 'name1',
                                             'test_bind_name2': 'name2',}
    app.config['AUX_DB_ENGINE_DISCOVERY_MAP'] = {'test_bind_name1': 'name1',
                                                 'test_bind_name2': 'name2',}
    app.config['BACKEND_API_URLS'] = {1: 'test_url1', 2: 'test_url2'}
    assert get_num_of_backends(app) == 2
