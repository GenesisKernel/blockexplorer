from flask import current_app as app

from ....logging import get_logger
#from ...db_engine.session import SessionManager, SessionManagerBase
from ...db_engine.engine import get_discovered_db_engines
#from ....utils import is_number

logger = get_logger(app)

class Error(Exception):
    pass

def update_aux_db_engine_discovery_map(app, **kwargs):
    map_name = kwargs.get('db_engine_discovery_map_name',
                                              'DB_ENGINE_DISCOVERY_MAP')

    aux_map_name = kwargs.get('aux_db_engine_discovery_map_name',
                              'AUX_DB_ENGINE_DISCOVERY_MAP')

    aux_prefix = kwargs.get('aux_db_engine_name_prefix', 'aux_',)
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
