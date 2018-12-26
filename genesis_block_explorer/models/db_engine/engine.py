from sqlalchemy.pool import StaticPool
from sqlalchemy import create_engine

from flask import current_app as app

from ...logging import get_logger
from ..utils import merge_two_dicts

logger = get_logger(app)

class Error(Exception): pass
class NoSuchConfigKeyError(Error): pass
class DbEngineMapIsEmptyError(Error): pass
class NoBindNameFoundError(Error): pass

def get_pq_engine_db_list(engine):
    if engine.name == "postgresql":
        q = engine.execute('SELECT datname FROM "pg_database";')
        db_names_list = [d[0] for d in q.fetchall()]
    elif engine.name == "sqlite":
        q = engine.execute('.databases')
        db_names_list = [d[0] for d in q.fetchall()]
    else:
        raise DatabaseUnknown(engine.name)

def db_engine_to_name(engine):
    if engine.name in ("postgresql", "mysql", "mssql"):
        db_name = str(engine.url).split('/')[-1]
    elif engine.name in ("sqlite",):
        db_name = str(engine.url).split('/')[-1]
        db_name_ar = db_name.split('.')
        if len(db_name_ar) > 1:
            db_name = '.'.join(db_name_ar[:-1])
    else:
        db_name = str(engine.url)
    return db_name

def get_discovered_db_engines(app, **kwargs):
    all_engines_options = kwargs.get('all_engines_options', {
        'convert_unicode': True,
        'encoding': 'utf-8',
    })
    db_engine_discovery_map_name = kwargs.get('db_engine_discovery_map_name',
                                              'DB_ENGINE_DISCOVERY_MAP')

    if db_engine_discovery_map_name in app.config:
        logger.info("%s exists" % db_engine_discovery_map_name)
        db_engine_discovery_map = app.config[db_engine_discovery_map_name]
    else:
        logger.info("%s isn't set or empty" % db_engine_discovery_map_name)
        db_engine_discovery_map = {}

    engines = {}
    for bind_name, info in db_engine_discovery_map.items():
        conn_uri = None
        if bind_name == 'SQLALCHEMY_DATABASE_URI' \
        and 'SQLALCHEMY_DATABASE_URI' in app.config:
            conn_uri = app.config['SQLALCHEMY_DATABASE_URI']
        elif 'SQLALCHEMY_BINDS' in app.config \
        and bind_name in app.config['SQLALCHEMY_BINDS']:
            conn_uri = app.config['SQLALCHEMY_BINDS'][bind_name]
        else:
            raise NoBindNameFoundError(bind_name)
        if info and 'engine_options' in info:
            engine_options = info['engine_options']
        else:
            engine_options = {}
        if all_engines_options:
            engine_options = merge_two_dicts(engine_options,
                                             all_engines_options)
        if conn_uri:
            if conn_uri == 'sqlite:///:memory:':
                engine_options.update({'connect_args': {'check_same_thread': False}, 'poolclass': StaticPool})
            engines[bind_name] = create_engine(conn_uri, **engine_options)
    
    return engines

def get_discovered_db_engine_info(bind_name, **kwargs):
    db_engine_discovery_map_name = kwargs.get('db_engine_discovery_map_name',
                                              'DB_ENGINE_DISCOVERY_MAP')
    if db_engine_discovery_map_name in app.config \
    and bind_name in app.config[db_engine_discovery_map_name] \
    and app.config[db_engine_discovery_map_name][bind_name]:
        return app.config[db_engine_discovery_map_name][bind_name]
    else:
        raise NoBindNameFoundError(bind_name)

def check_db_engine_discovery_map(app, **kwargs):
    db_engine_discovery_map_name = kwargs.get('db_engine_discovery_map_name',
                                              'DB_ENGINE_DISCOVERY_MAP')
    db_engine_discovery_map = app.config.get(db_engine_discovery_map_name)
    if db_engine_discovery_map_name not in app.config:
        raise NoSuchConfigKeyError(db_engine_discovery_map_name)
    if not tuple(db_engine_discovery_map.keys()):
        raise DbEngineMapIsEmptyError()
