from flask import current_app as app

from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import inspect 

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

class SessionManager:
    def __init__(self, **kwargs):
        self.app = kwargs.get('app', None)
        self.engines = kwargs.get('engines', [])
        self.engines_discovered = False
        self.sessions = kwargs.get('sessions', [])
        self.sessions_created = False
        self.database = kwargs.get('database', Database)

    def discover_engines(self):
        self.engines = get_discovered_db_engines(self.app)

    def create_sessions(self):
        self.sessions = create_sessions_for_engines(self.engines)

    def init_sessions_and_engines(self):
        if not self.engines_discovered:
            self.discover_engines()
        if not self.sessions_created:
            self.create_sessions()

    def get_db(self, db_id):
        self.init_sessions_and_engines()
        return self.database.query.get(db_id)

    def get(self, db_id):
        db = self.get_db(db_id)
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
        return get_discovered_db_engine_info(bind_name)

    def get_be_version(self, db_id):
        db = self.get_db(db_id)
        return db.backend_version

    def get_be_features(self, db_id):
        backend_version = self.get_be_version(db_id)
        return get_backend_features_by_version(int(backend_version))

