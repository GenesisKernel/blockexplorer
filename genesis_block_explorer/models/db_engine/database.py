from pprint import pprint

import types
import pickle 
import six

from dictalchemy import make_class_dictable

from sqlalchemy import inspect 
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from sqlalchemy.types import *
from sqlalchemy.exc import OperationalError

from sqlalchemy.ext.declarative import declarative_base
from flask_jsontools import JsonSerializableBase

from .autoser import AutoSerialize
from ...logging import get_logger
from .engine import (
    db_engine_to_name,
    get_discovered_db_engines,
    get_discovered_db_engine_info,
)

Base = declarative_base()
logger = get_logger()

from ...debug_utils import (
    get_function_name as _fn,
    get_function_name2 as _fn2,
    get_function_parameters_and_values as _fpav,
    get_class_name_of_function as _cnof,
    get_class_and_function_names as _cafn,
    get_function_name_and_parameters_and_values as _fnapav,
    get_class_and_function_names_and_parameters_and_values as _cafnapav,
)

from ...db import db

from ...utils import is_number, semirepr

#from .automap import Base

class DatabaseError(Exception):
    pass

class DatabaseUnknown(DatabaseError):
    pass

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
    engines = kwargs.get('engines', None)
    if not engines:
        engines = get_discovered_db_engines(app)
    for bind_name, engine in engines.items(): 
        try:
            inspector = inspect(engine)
        except OperationalError as e:
            logger.error("cant inspect engine %s" % engine)
            continue
        except Exception as e:
            raise e
        db_name = db_engine_to_name(engine)
        info = get_discovered_db_engine_info(bind_name)
        backend_version = ''
        if info:
            try:
                backend_version = info['backend_version']
            except TypeError as e:
                pass
            except KeyError as e:
                pass
            except Exception as e:
                raise e

        logger.debug("bind_name: %s engine: %s db_name: %s" \
                    % (bind_name, engine, db_name))
        d = Database(name=db_name, bind_name=bind_name,
                     engine=engine.name, driver=engine.driver,
                     backend_version=backend_version)
        for table_name in inspector.get_table_names():
            logger.debug("table_name: %s" % (table_name,))
            t = Table(name=table_name)
            for column in inspector.get_columns(table_name):
                c = Column(**column)
                t.columns.append(c)
            d.tables.append(t)
        db.session.add(d)
    db.session.commit()

