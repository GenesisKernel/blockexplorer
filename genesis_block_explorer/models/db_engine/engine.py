from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import (
    create_engine
)

from flask import current_app as app

from ...logging import get_logger

logger = get_logger(app)

def merge_two_dicts(x, y):
    """Given two dicts, merge them into a new dict as a shallow copy."""
    z = x.copy()
    z.update(y)
    return z

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

def get_discovered_db_engines_old(app, **kwargs):
    engine_options = kwargs.get('engine_options', {
        'convert_unicode': True,
        'encoding': 'utf-8',
    })
    if 'DB_ENGINE_DISCOVERY_MAP' in app.config:
        logger.error("HERE DB_ENGINE_DISCOVERY_MAP mode")
        db_engine_discovery_map = app.config['DB_ENGINE_DISCOVERY_MAP']
        logger.error("db_engine_discovery_map: %s" %  db_engine_discovery_map)
    else:
        db_engine_discovery_map = {}
        if 'SQLALCHEMY_DATABASE_URI' in app.config:
            db_engine_discovery_map['SQLALCHEMY_DATABASE_URI'] \
                    = app.config['SQLALCHEMY_DATABASE_URI']
        else:
            db_engine_discovery_map['SQLALCHEMY_DATABASE_URI'] = None

        if 'SQLALCHEMY_BINDS' in app.config:
            db_engine_discovery_map['SQLALCHEMY_BINDS'] \
                    = app.config['SQLALCHEMY_BINDS']
        else:
            db_engine_discovery_map['SQLALCHEMY_BINDS'] = {}

    engines = {}
    if 'SQLALCHEMY_DATABASE_URI' in db_engine_discovery_map:
        engines['SQLALCHEMY_DATABASE_URI'] = create_engine(
                    db_engine_discovery_map['SQLALCHEMY_DATABASE_URI'],
                    **engine_options
                    )

    if 'SQLALCHEMY_BINDS' in db_engine_discovery_map \
            and db_engine_discovery_map['SQLALCHEMY_BINDS']:
                engines = merge_two_dicts(
                    engines,
                    {k: create_engine(v, **engine_options) for k, v in \
                        db_engine_discovery_map['SQLALCHEMY_BINDS'].items()})
    logger.error("engines: %s" % engines)
    return engines

def get_discovered_db_engines(app, **kwargs):
    all_engines_options = kwargs.get('all_engines_options', {
        'convert_unicode': True,
        'encoding': 'utf-8',
    })

    if 'DB_ENGINE_DISCOVERY_MAP' in app.config:
        logger.error("DB_ENGINE_DISCOVERY_MAP exists")
        db_engine_discovery_map = app.config['DB_ENGINE_DISCOVERY_MAP']
    else:
        logger.error("DB_ENGINE_DISCOVERY_MAP isn't set or empty")
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
        if info and 'engine_options' in info:
            engine_options = info['engine_options']
        else:
            engine_options = {}
        if all_engines_options:
            engine_options = merge_two_dicts(engine_options,
                                             all_engines_options)
        if conn_uri:
            engines[bind_name] = create_engine(conn_uri, **engine_options)
    
    return engines

def get_discovered_db_engine_info(bind_name):
    if 'DB_ENGINE_DISCOVERY_MAP' in app.config \
    and bind_name in app.config['DB_ENGINE_DISCOVERY_MAP'] \
    and app.config['DB_ENGINE_DISCOVERY_MAP'][bind_name]:
        return app.config['DB_ENGINE_DISCOVERY_MAP'][bind_name]

