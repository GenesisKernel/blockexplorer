from sqlalchemy import exc

from flask import current_app as app

from ....process import check_pid
from ....logging import get_logger
from ...db_engine.session import SessionManager
from ...db_engine.seq_num import get_valid_seq_num
from .session import AuxSessionManager
from .lock import LockModel
from .log import LogModel

logger = get_logger(app) 

class Error(Exception):
    pass

class FillerIsLockedError(Error):
    pass

class Filler:
    def __init__(self, **kwargs):
        self.base_models = kwargs.get('base_models', [LockModel, LogModel])
        self.involved_models = kwargs.get('involved_models', [])
        self.app = kwargs.get('app', None)
        self.db_engine_discovery_map_name=kwargs.get('db_engine_discovery_map_name', 'AUX_DB_ENGINE_DISCOVERY_MAP')
        self.seq_num = get_valid_seq_num(self.app, kwargs.get('seq_num', 1),
            db_engine_discovery_map_name=self.db_engine_discovery_map_name)
        self.create_tables = kwargs.get('create_tables', True)
        self.recreate_tables_if_exist = kwargs.get('recreate_tables_if_exist',
                                                   False)
        self.bc_sm = SessionManager(app=self.app)
        self.aux_sm = AuxSessionManager(app=self.app)
        self.context = kwargs.get('Filler',
                                  'Filler_%s' if self.seq_num else 'Filler')
        self.caller = 'default_filler_caller'
        self.clear_lock_garbage = kwargs.get('self.clear_lock_garbage', True)
        if self.create_tables:
            self.do_create_tables()

    def do_create_tables(self, **kwargs):
        recreate_tables_if_exist = kwargs.get('recreate_tables_if_exist', 
                                              self.recreate_tables_if_exist)
        engine = self.aux_sm.get_engine(self.seq_num)
        for model in self.base_models + self.involved_models:
            if recreate_tables_if_exist:
                try:
                    model.__table__.drop(engine)
                except exc.OperationalError as e:
                    logger.info("Recreate if exists mode: can't drop table for model %s, error: %s" % (model, e))
            try:
                model.__table__.create(engine)
            except exc.OperationalError as e:
                logger.info("Can'n create table for model %s, error: %s" % (model, e))

    def check_dbs(self):
        assert len(self.bc_sm.engines) == len(self.aux_sm.engines)
        assert len(self.bc_sm.sessions) == len(self.aux_sm.sessions)

    def add_event(self, **kwargs):
        caller = kwargs.get('caller', self.caller)
        stage = kwargs.get('stage')
        return LogModel.add(session=self.aux_sm.get(self.seq_num),
                            context=self.context, caller=caller,
                            stage=stage)

    @property
    def is_locked(self):
        if self.clear_lock_garbage:
            LockModel.clear_garbage(session=self.aux_sm.get(self.seq_num),
                                   context=self.context)
        return LockModel.is_locked(session=self.aux_sm.get(self.seq_num),
                                   context=self.context)

    @property
    def latest_lock(self, **kwargs):
        if self.clear_lock_garbage:
            LockModel.clear_garbage(session=self.aux_sm.get(self.seq_num),
                                   context=self.context)
        return LockModel.get_latest_lock(session=self.aux_sm.get(self.seq_num),
                                         context=self.context)

    def lock(self, **kwargs):
        if self.clear_lock_garbage:
            LockModel.clear_garbage(session=self.aux_sm.get(self.seq_num),
                                   context=self.context)
        if kwargs.get('disable_locking', False):
            return
        return LockModel.lock(session=self.aux_sm.get(self.seq_num),
                              context=self.context)

    def unlock(self, **kwargs):
        if self.clear_lock_garbage:
            LockModel.clear_garbage(session=self.aux_sm.get(self.seq_num),
                                   context=self.context)
        if kwargs.get('disable_locking', False):
            return
        return LockModel.unlock(session=self.aux_sm.get(self.seq_num),
                                context=self.context)

    def do_if_locked(self, **kwargs):
        if kwargs.get('disable_locking', False):
            return
        if self.is_locked:
            msg = "Filler is locked."
            if self.latest_lock:
                msg += " Lock info: Date/Time: %s, PID: %d, Context: %s, Engine: %s, Session: %s, Process Alive: %s" % (self.latest_lock.created_at, self.latest_lock.process_id, self.latest_lock.context, self.aux_sm.get_engine(self.seq_num), self.aux_sm.get(self.seq_num), check_pid(self.latest_lock.process_id))
            else:
                msg += " No lock info available."
            logger.warning(msg)
            raise FillerIsLockedError(msg)

