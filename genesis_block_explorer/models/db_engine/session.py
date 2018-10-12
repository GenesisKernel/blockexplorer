from flask import current_app as app

from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import inspect 

from .seq_num import get_valid_seq_num
from ...logging import get_logger
from .database import Database
from .engine import get_discovered_db_engines, get_discovered_db_engine_info
from ...utils import get_backend_features_by_version

logger = get_logger(app)

def create_sessions_for_engines(engines, **kwargs):
    sessions = {}
    for bind_name, engine in engines.items():
        sessions[bind_name] = {}
        sessions[bind_name]['session_class'] = scoped_session(sessionmaker(bind=engine)) 
        sessions[bind_name]['session'] = sessions[bind_name]['session_class']()
    return sessions

class SessionManagerBase:
    def __init__(self, **kwargs):
        self.app = kwargs.get('app', None)
        self.engines = kwargs.get('engines', [])
        self.engines_discovered = kwargs.get('engines_discovered', False)
        self.sessions = kwargs.get('sessions', [])
        self.sessions_created = kwargs.get('sessions_created', False)
        self.init_sessions_and_engines()

    def discover_engines(self):
        self.engines = get_discovered_db_engines(self.app,
                 db_engine_discovery_map_name=self.db_engine_discovery_map_name)
        logger.debug("discover_engines: %s" % self.engines)

    def create_sessions(self):
        self.sessions = create_sessions_for_engines(self.engines)
        logger.debug("created sessions: %s" % self.sessions)

    def init_sessions_and_engines(self):
        if not self.engines_discovered:
            self.discover_engines()
        if not self.sessions_created:
            self.create_sessions()

    def get(self, key):
        return self.get_session(key)

class SessionManagerOld(SessionManagerBase):
    def __init__(self, **kwargs):
        self.db_engine_discovery_map_name = \
            kwargs.get('db_engine_discovery_map_name',
                       'DB_ENGINE_DISCOVERY_MAP')
        super(SessionManager, self).__init__(**kwargs)
        self.database = kwargs.get('database', Database)

    def get_db(self, db_id):
        return self.database.query.get(db_id)

    def get_session(self, db_id):
        db = self.get_db(db_id)
        logger.debug("db: %s, db.bind_name: %s" %(db, db.bind_name))
        return self.sessions[db.bind_name]['session']

    def get_engine(self, db_id):
        db = self.get_db(db_id)
        return self.engines[db.bind_name]

    def get_inspector(self, db_id):
        engine = self.get_engine(db_id)
        return inspect(engine)

    def get_table_names(self, db_id):
        return self.get_inspector(db_id).get_table_names()

    def get_be_info(self, db_id):
        db = self.get_db(db_id)
        bind_name = db.bind_name
        return get_discovered_db_engine_info(bind_name,
                 db_engine_discovery_map_name=self.db_engine_discovery_map_name)

    def get_be_version(self, db_id):
        db = self.get_db(db_id)
        return db.backend_version

    def get_be_features(self, db_id):
        backend_version = self.get_be_version(db_id)
        #return get_backend_features_by_version(int(backend_version))
        return get_backend_features_by_version(backend_version)

class SessionManager(SessionManagerBase):
    def __init__(self, **kwargs):
        self.db_engine_discovery_map_name = \
            kwargs.get('db_engine_discovery_map_name',
                       'DB_ENGINE_DISCOVERY_MAP')
        super(SessionManager, self).__init__(**kwargs)

    def get_bind_name(self, seq_num):
        seq_num = get_valid_seq_num(self.app, seq_num,
            db_engine_discovery_map_name=self.db_engine_discovery_map_name)
        _map = self.app.config.get(self.db_engine_discovery_map_name)
        key = tuple(_map.keys())[seq_num - 1]
        return key

    def get_session(self, seq_num):
        bind_name = self.get_bind_name(seq_num)
        logger.debug("bind_name: %s" % bind_name)
        return self.sessions[bind_name]['session']

    def get_engine(self, seq_num):
        bind_name = self.get_bind_name(seq_num)
        logger.debug("bind_name: %s" % bind_name)
        return self.engines[bind_name]

    def get_inspector(self, seq_num):
        seq_num = get_valid_seq_num(self.app, seq_num,
            db_engine_discovery_map_name=self.db_engine_discovery_map_name)
        bind_name = self.get_bind_name(seq_num)
        logger.debug("bind_name: %s" % bind_name)
        engine = self.get_engine(seq_num)
        return inspect(engine)

    def get_table_names(self, seq_num):
        seq_num = get_valid_seq_num(app, seq_num,
            db_engine_discovery_map_name=self.db_engine_discovery_map_name)
        return self.get_inspector(seq_num).get_table_names()

    def get_be_info(self, seq_num):
        bind_name = self.get_bind_name(seq_num)
        logger.debug("bind_name: %s" % bind_name)
        return get_discovered_db_engine_info(bind_name,
                 db_engine_discovery_map_name=self.db_engine_discovery_map_name)

    def get_be_version(self, seq_num):
        seq_num = get_valid_seq_num(app, seq_num,
            db_engine_discovery_map_name=self.db_engine_discovery_map_name)
        bind_name = self.get_bind_name(seq_num)
        _map = self.app.config.get(self.db_engine_discovery_map_name)
        return _map[bind_name]['backend_version']

    def get_be_features(self, seq_num):
        backend_version = self.get_be_version(seq_num)
        #print("get_be_features 1 backend_version: %s "% backend_version)
        return get_backend_features_by_version(backend_version)
