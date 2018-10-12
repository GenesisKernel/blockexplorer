from sqlalchemy.pool import StaticPool
from sqlalchemy import create_engine

from flask import current_app as app

from ....logging import get_logger
from ...utils import merge_two_dicts
from ...db_engine.engine import (
    get_discovered_db_engines as _get_discovered_db_engines,
    get_discovered_db_engine_info as _get_discovered_db_engine_info,
    NoBindNameFoundError,
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

def get_aux_helpers_engine(app, **kwargs):
    aux_helpers_bind_name_name = kwargs.get('aux_helpers_bind_name_name',
                                            'AUX_HELPERS_BIND_NAME')
    bind_name = app.config.get(aux_helpers_bind_name_name)
    engine_options = kwargs.get('engine_options', {
        'convert_unicode': True,
        'encoding': 'utf-8',
    })
    conn_uri = None
    if bind_name == 'SQLALCHEMY_DATABASE_URI' \
    and 'SQLALCHEMY_DATABASE_URI' in app.config:
        conn_uri = app.config['SQLALCHEMY_DATABASE_URI']
    elif 'SQLALCHEMY_BINDS' in app.config \
    and bind_name in app.config['SQLALCHEMY_BINDS']:
        conn_uri = app.config['SQLALCHEMY_BINDS'][bind_name]
    else:
        raise NoBindNameFoundError(bind_name)
    if conn_uri == 'sqlite:///:memory:' or conn_uri == 'sqlite://':
        engine_options.update({'connect_args': {'check_same_thread': False}, 'poolclass': StaticPool})
    return create_engine(conn_uri, **engine_options)
