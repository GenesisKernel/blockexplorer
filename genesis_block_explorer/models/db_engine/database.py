from pprint import pprint

import types
import pickle 
import six
import logging
from diskcache import Cache

from dictalchemy import make_class_dictable

from sqlalchemy import inspect 
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from sqlalchemy.exc import OperationalError

from sqlalchemy.ext.declarative import declarative_base

from flask_jsontools import JsonSerializableBase

from ...logging import get_logger
from .engine import (
    db_engine_to_name,
    get_discovered_db_engines,
    get_discovered_db_engine_info,
    NoBindNameFoundError,
)

logger = logging.getLogger(__name__)

from ...db import db

from ...utils import is_number, semirepr

class Error(Exception): pass
class AppIsNotSetError(Error): pass
class DatabaseError(Exception): pass
class DatabaseUnknown(DatabaseError): pass

class Database(db.Model):

    __bind_key__ = 'db_engine'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    bind_name = db.Column(db.String)
    engine = db.Column(db.String)
    driver = db.Column(db.String)
    backend_version = db.Column(db.String)
    tables = db.relationship('Table', uselist=True,
                             backref=db.backref('database'))

    @hybrid_property
    def tables_ids_names(self):
        return [t.id_name for t in self.tables]

    def __unicode__(self):
        """Give a readable representation of an instance."""
        return '%s' % self.name

    def __repr__(self):
        """Give a unambiguous representation of an instance."""
        return '<%s#%s>' % (self.__class__.__name__, self.id)

    def as_dict(self):
        d = {}
        names = ('name', 'engine', 'driver', 'bind_name', 'backend_version')
        for name in names:
            d[name] = getattr(self, name)
        d['tables'] = [t.as_dict() for t in self.tables]
        return d

    @classmethod
    def add_from_engine(cls, engine, **kwargs):
        app = kwargs.get('app')
        session = kwargs.get('session', db.session)
        bind_name = kwargs.get('bind_name')
        backend_version = kwargs.get('backend_version')

        use_cache = kwargs.get('use_cache', False) and app
        if use_cache:
            flush_cache = kwargs.get('flush_cache', False)
            cache_path = kwargs.get('cache_path',
                                    app.config.get('DISKCACHE_PATH'))
            cache_timeout = kwargs.get('DISKCACHE_DBEX_DATABASE_TIMEOUT')
            cache = Cache(cache_path)
            if flush_cache:
                cache.pop(engine)

        try:
            if use_cache:
                inspector = cache.get(engine)
            else:
                inspector = inspect(engine)
                if use_cache:
                    cache.set(engine, inspector, cache_timeout)
        except OperationalError as e:
            logger.error("cant inspect engine %s" % engine)
            raise e
        except Exception as e:
            raise e
        db_name = db_engine_to_name(engine)
        try:
            info = get_discovered_db_engine_info(bind_name)
        except NoBindNameFoundError:
            logger.warning("No info found to engine bind name '%s'" % bind_name)
            info = ''
        if not backend_version and info:
            try:
                backend_version = info['backend_version']
            except TypeError as e:
                pass
            except KeyError as e:
                pass
            except Exception as e:
                raise e

        d = Database(name=db_name, bind_name=bind_name, engine=engine.name,
                     driver=engine.driver, backend_version=backend_version)
        table_names = inspector.get_table_names()
        for table_name in table_names:
            logger.debug("table_name: %s" % (table_name,))
            t = Table(name=table_name)
            column_names = inspector.get_columns(table_name)
            for column in column_names:
                c = Column(**column)
                t.columns.append(c)
            d.tables.append(t)
        session.add(d)
        if kwargs.get('db_session_commit_enabled', True):
            session.commit()

    @classmethod
    def add_from_engines(cls, **kwargs):
        engines = kwargs.get('engines', None)
        app = kwargs.get('app')
        db_engine_discovery_map_name = \
          kwargs.get( 'db_engine_discovery_map_name', 'DB_ENGINE_DISCOVERY_MAP')
        if not engines:
            if app:
                engines = get_discovered_db_engines(app,
                      db_engine_discovery_map_name=db_engine_discovery_map_name)
            else:
                raise AppIsNotSetError
        logger.debug("engines: %s " % engines)
        if type(engines) in (list, tuple):
            for engine in engines:
                add_from_engine(engine)
        elif type(engines) == dict:
            for bind_name, engine in engines.items(): 
                cls.add_from_engine(engine, app=app, bind_name=bind_name)

class Table(db.Model):

    __bind_key__ = 'db_engine'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    database_id = db.Column(db.Integer, db.ForeignKey('database.id'))
    columns = db.relationship('Column', uselist=True,
                              backref=db.backref('table'))

    @hybrid_property
    def id_name(self):
        return (self.id, self.name,)

    def __unicode__(self):
        """Give a readable representation of an instance."""
        return '%s' % self.name

    def __repr__(self):
        """Give a unambiguous representation of an instance."""
        return '<%s#%s>' % (self.__class__.__name__, self.id)

    def as_dict(self):
        d = {}
        names = ('name', 'database_id')
        for name in names:
            d[name] = getattr(self, name)
        d['columns'] = [c.as_dict() for c in self.columns]
        return d

class Column(db.Model):

    __bind_key__ = 'db_engine'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    _type_repr = db.Column(db.String)
    _type_pickle = db.Column(db.PickleType)
    nullable = db.Column(db.Boolean)
    _default_repr = db.Column(db.String)
    _default_pickle = db.Column(db.PickleType)
    _autoincrement_repr = db.Column(db.String)
    _autoincrement_pickle = db.Column(db.PickleType)
    comment = db.Column(db.Boolean)
    primary_key = db.Column(db.Integer)
    _unknown_params = db.Column(db.PickleType)
    table_id = db.Column(db.Integer, db.ForeignKey('table.id'))

    _KNOWN_PARAMS=('name', 'type', 'nullable', 'default', 'autoincrement',
                  'comment', 'primary_key')
    _SKIP_PARAMS = ('id',)
    _SPECIAL_PARAMS=('type', 'default', 'autoincrement',)

    @hybrid_property
    def type(self):
        return self._type_repr

    @hybrid_property
    def type_raw(self):
        if self._type_pickle:
            obj = pickle.loads(self._type_pickle)
            return obj

    @type.setter
    def type(self, value):
        self._type_pickle = pickle.dumps(value)
        self._type_repr = semirepr(value)


    @hybrid_property
    def default(self):
        return self._default_repr

    @hybrid_property
    def default_raw(self):
        if self._default_pickle:
            obj = pickle.loads(self._default_pickle)
            return obj

    @default.setter
    def default(self, value):
        self._default_pickle = pickle.dumps(value)
        self._default_repr = semirepr(value)

    @hybrid_property
    def autoincrement(self):
        return self._autoincrement_repr

    @hybrid_property
    def autoincrement_raw(self):
        if self._autoincrement_pickle:
            obj = pickle.loads(self._autoincrement_pickle)
            return obj

    @autoincrement.setter
    def autoincrement(self, value):
        self._autoincrement_pickle = pickle.dumps(value)
        self._autoincrement_repr = semirepr(value)


    def __init__(self, **kwargs):
        known_params = {}
        special_params = {}
        unknown_params = {}
        for name, value in kwargs.items():
            if name in self._SKIP_PARAMS:
                continue
            if name in self._KNOWN_PARAMS:
                if name in self._SPECIAL_PARAMS:
                    special_params[name] = value
                    logger.debug("known param %s=%s" % (name, value))
                    setattr(self, name, value)
                else:
                    known_params[name] = value
            else:
                unknown_params[name] = value
        super(self.__class__, self).__init__(**known_params)
        for name, value in special_params.items():
            logger.debug("special param %s=%s" % (name, value))
            setattr(self, name, value)

    def __unicode__(self):
        """Give a readable representation of an instance."""
        return '%s' % self.name

    def __repr__(self):
        """Give a unambiguous representation of an instance."""
        return '<%s#%s>' % (self.__class__.__name__, self.id)

    def as_dict(self):
        d = {}
        names = self._KNOWN_PARAMS + self._SKIP_PARAMS + self._SPECIAL_PARAMS
        for name in names:
            d[name] = getattr(self, name)
        return d

def init_db():
    db.create_all(bind='db_engine')

def import_data(app, **kwargs):
    Column.query.delete()
    Table.query.delete()
    Database.query.delete()
    Database.add_from_engines(app=app)

