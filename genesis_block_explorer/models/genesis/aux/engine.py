from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import (
    create_engine
)

from flask import current_app as app

from ....logging import get_logger
from ...utils import merge_two_dicts
from ...db_engine.engine import (
    get_discovered_db_engines as _get_discovered_db_engines,
    get_discovered_db_engine_info as _get_discovered_db_engine_info,
)

logger = get_logger(app)

def get_aux_db_engines(app, **kwargs):
    kwargs['db_engine_discovery_map_name'] = kwargs.get(
                                                 'db_engine_discovery_map_name',
                                                 'AUX_DB_ENGINE_DISCOVERY_MAP')
    return _get_discovered_db_engines(app, **kwargs)

def get_aux_db_engine_info(bind_name, **kwargs):
    kwargs['db_engine_discovery_map_name'] = kwargs.get(
                                                 'db_engine_discovery_map_name',
                                                 'AUX_DB_ENGINE_DISCOVERY_MAP')
    return _get_discovered_db_engine_info(bind_name, **kwargs)
