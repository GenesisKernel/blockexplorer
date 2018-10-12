from flask import current_app as app

from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import inspect 

from ....logging import get_logger
from ...db_engine.seq_num import get_valid_seq_num
from ...db_engine.session import (
    SessionManager, SessionManagerBase, create_sessions_for_engines,
)
from ....utils import is_number
from .engine import get_aux_helpers_engine

logger = get_logger(app)

class AuxSessionManager(SessionManagerBase):
    def __init__(self, **kwargs):
        self.db_engine_discovery_map_name = \
            kwargs.get('db_engine_discovery_map_name',
                       'AUX_DB_ENGINE_DISCOVERY_MAP')
        super(AuxSessionManager, self).__init__(**kwargs)

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
        bind_name = sef.get_bind_name(seq_num)
        logger.debug("bind_name: %s" % bind_name)
        engine = self.get_engine(seq_num)
        return inspect(engine)

    def get_table_names(self, seq_num):
        seq_num = get_valid_seq_num(app, seq_num,
            db_engine_discovery_map_name=self.db_engine_discovery_map_name)
        return self.get_inspector(seq_num).get_table_names()

    def get_be_info(self, seq_num):
        bind_name = sef.get_bind_name(seq_num)
        logger.debug("bind_name: %s" % bind_name)
        return get_discovered_db_engine_info(bind_name,
                 db_engine_discovery_map_name=self.db_engine_discovery_map_name)

    def get_be_version(self, seq_num):
        seq_num = get_valid_seq_num(app, seq_num,
            db_engine_discovery_map_name=self.db_engine_discovery_map_name)
        bind_name = sef.get_bind_name(seq_num)
        _map = self.app.config.get(self.db_engine_discovery_map_name)
        return _map[bind_name]

    def get_be_features(self, seq_num):
        backend_version = self.get_be_version(seq_num)
        return get_backend_features_by_version(backend_version)

def get_aux_helpers_session(app, **kwargs): 
    aux_helper_bind_name_name = kwargs.get('aux_helper_bind_name_name',
                                           'AUX_HELPER_BIND_NAME')
    engines = {aux_helper_bind_name_name: get_aux_helpers_engine(app,
                        aux_helper_bind_name_name=aux_helper_bind_name_name)}
    sessions = create_sessions_for_engines(engines)
    return sessions[aux_helper_bind_name_name]['session']

