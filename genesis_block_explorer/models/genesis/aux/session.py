from flask import current_app as app
#from .engine import db_engine.engine

from ....logging import get_logger
from ...db_engine.session import SessionManager, SessionManagerBase
from ....utils import is_number

logger = get_logger(app)

class Error(Exception):
    pass

class DbEngineMapIsEmptyError(Error):
    pass

class WrongDbSeqNumError(Error):
    pass

class NoSuchConfigKeyError(Error):
    pass

class AuxSessionManager(SessionManagerBase):
    def __init__(self, **kwargs):
        self.db_engine_discovery_map_name = \
            kwargs.get('db_engine_discovery_map_name',
                       'AUX_DB_ENGINE_DISCOVERY_MAP')
        super(AuxSessionManager, self).__init__(**kwargs)

    def check_seq_num(self, seq_num, _map = {}):
        _map = self.app.config.get(self.db_engine_discovery_map_name)
        if self.db_engine_discovery_map_name not in self.app.config:
            raise NoSuchConfigKeyError(self.db_engine_discovery_map_name)
        if not is_number(seq_num):
            raise WrongDbSeqNumError("'%s' provided as database sequence number, but shoud be a number >= 1 nad <= %d" % (seq_num, len(_map)))
        keys = tuple(_map.keys())
        if not keys:
            raise DbEngineMapIsEmptyError()
        if seq_num <= 0 or seq_num > len(_map):
            raise WrongDbSeqNumError("'%s' provided as database sequence number, but shoud be a number >= 1 and <= %d" % (seq_num, len(_map)))

    def get_bind_name(self, seq_num):
        self.check_seq_num(seq_num)
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
        bind_name = sef.get_bind_name(seq_num)
        logger.debug("bind_name: %s" % bind_name)
        engine = self.get_engine(seq_num)
        return inspect(engine)

    def get_table_names(self, seq_num):
        return self.get_inspector(seq_num).get_table_names()

    def get_be_info(self, seq_num):
        bind_name = sef.get_bind_name(seq_num)
        logger.debug("bind_name: %s" % bind_name)
        return get_discovered_db_engine_info(bind_name,
                 db_engine_discovery_map_name=self.db_engine_discovery_map_name)

    def get_be_version(self, seq_num):
        self.check_seq_num(seq_num)
        bind_name = sef.get_bind_name(seq_num)
        _map = self.app.config.get(self.db_engine_discovery_map_name)
        return _map[bind_name]

    def get_be_features(self, seq_num):
        backend_version = self.get_be_version(seq_num)
        #return get_backend_features_by_version(int(backend_version))
        return get_backend_features_by_version(backend_version)

