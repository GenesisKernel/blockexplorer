from flask import current_app as app

from ....logging import get_logger

logger = get_logger(app)

def update_aux_db_engine_discovery_map(app, **kwargs):
    map_name = kwargs.get('db_engine_discovery_map_name',
                                              'DB_ENGINE_DISCOVERY_MAP')

    aux_map_name = kwargs.get('aux_db_engine_discovery_map_name',
                              'AUX_DB_ENGINE_DISCOVERY_MAP')

    aux_prefix = kwargs.get('aux_db_engine_name_prefix', 'aux_')
    force_update = kwargs.get('force_update', False)

    aux_map = app.config.get(aux_map_name)
    _map = app.config.get(map_name)

    if force_update:
        logger.warning("forcing aux map configuration updating")
    if not aux_map or force_update:
        new_aux_map = {}
        for bind_name, backend_config in _map.items():
            new_aux_map[aux_prefix + bind_name] = backend_config
        app.config[aux_map_name] = new_aux_map
    return app.config.get(aux_map_name)

def update_aux_helpers_bind_name(app, **kwargs):
    aux_helpers_bind_name_name = kwargs.get('aux_helpers_bind_name_name',
                                            'AUX_HELPERS_BIND_NAME')
    prefix = kwargs.get('prefix', '')

    aux_helpers_bind_name = app.config.get(aux_helpers_bind_name_name)
    new_aux_helpers_bind_name = prefix + aux_helpers_bind_name
    app.config[aux_helpers_bind_name_name] = new_aux_helpers_bind_name 
    return app.config.get(aux_helpers_bind_name_name)

def get_num_of_backends(app, **kwargs):
    map_name = kwargs.get('db_engine_discovery_map_name',
                                              'DB_ENGINE_DISCOVERY_MAP')
    db_map = app.config.get(map_name, [])

    aux_map_name = kwargs.get('aux_db_engine_discovery_map_name',
                              'AUX_DB_ENGINE_DISCOVERY_MAP')
    aux_map = app.config.get(aux_map_name, [])

    backend_api_urls_name = kwargs.get('backend_api_urls_name',
                                       'BACKEND_API_URLS')

    api_urls = app.config.get(backend_api_urls_name, [])

    return min([len(db_map), len(db_map), len(api_urls)])

