from nose import with_setup

from genesis_block_explorer.models.genesis.aux.config import (
    update_aux_db_engine_discovery_map
)

def create_test_app():
    from genesis_block_explorer.app import create_app
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

