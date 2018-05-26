import datetime

from sqlalchemy import MetaData, Table, Column
from sqlalchemy import create_engine
from sqlalchemy.orm import column_property, public_factory
from sqlalchemy.orm.properties import ColumnProperty
from sqlalchemy.sql import select
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from sqlalchemy import func, desc

from flask import current_app as app

from ...logging import get_logger
from ...db import db
from ...models.db_engine.session import SessionManager

logger = get_logger(app)
sm = SessionManager(app=app)
    
backend_features = []

class Error(Exception):
    pass

class NoSuchEcosystem(Error):
    pass

class BlockChain(db.Model):

    __tablename__ = 'block_chain'
    __table_args__ = {'extend_existing': True}
    __bind_key__ = None

    id = db.Column(db.Integer, primary_key=True)
    hash = db.Column(db.LargeBinary)
    rollbacks_hash = db.Column(db.LargeBinary)
    data = db.Column(db.LargeBinary)
    ecosystem_id = db.Column(db.Integer)
    key_id = db.Column(db.BigInteger)
    node_position = db.Column(db.BigInteger)
    time = db.Column(db.Integer)
    tx = db.Column(db.Integer)

    @hybrid_method
    def next(self, **kwargs):
        db_id = kwargs.get('db_id')
        model = self.__class__
        return model.query.with_session(sm.get(db_id)).filter(model.id > self.id).order_by(model.id).first()

    @hybrid_method
    def has_next(self, **kwargs):
        if self.next(**kwargs):
            return True
        else:
            return False

    @hybrid_method
    def prev(self, **kwargs):
        db_id = kwargs.get('db_id')
        model = self.__class__
        return model.query.with_session(sm.get(db_id)).filter(model.id < self.id).order_by(desc(model.id)).first()

    @hybrid_method
    def has_prev(self, **kwargs):
        if self.prev(**kwargs):
            return True
        else:
            return False

    @hybrid_property
    def hash_hex(self):
        return self.hash.hex()

    @hash_hex.expression
    def hash_hex(self):
        return func.hex(self.hash)

    def __unicode__(self):
        """Give a readable representation of an instance."""
        return '%s' % self.name

    def __repr__(self):
        """Give a unambiguous representation of an instance."""
        return '<%s#%s>' % (self.__class__.__name__, self.id)

    def as_dict(self):
        d = {}
        names = ('id', 'hash', 'rollbacks_hash', 'data', 'ecosystem_id',
                 'key_id', 'node_position', 'time', 'tx',)
        for name in names:
            d[name] = getattr(self, name)
        return d

class TransactionsStatus(db.Model):

    __tablename__ = 'transactions_status'
    #__table_args__ = {'extend_existing': True}
    __bind_key__ = None

    #id = db.Column(db.Integer, primary_key=True)
    hash = db.Column(db.LargeBinary, primary_key=True)
    time = db.Column(db.Integer)
    type  = db.Column(db.Integer)
    ecosystem = db.Column(db.Integer)
    wallet_id = db.Column(db.BigInteger)
    block_id = db.Column(db.Integer)
    error = db.Column(db.String)


class EsModel(db.Model):
    __abstract__ = True
    #__table_args__ = {'extend_existing': True}
    _default_ecosystem_id_ = '1'
    __bind_key__ = None

    @classmethod
    def set_ecosystem(cls, ecosystem_id, **kwargs):
        table_name = '%d%s' % (ecosystem_id, cls._tablename_suffix_)
        db_id = kwargs.get('db_id', None)
        if db_id:
            if kwargs.get('use_inspector', False):
                table_names = sm.get_table_names(db_id)
            else:
                table_names = [t.name for t in sm.get_db(1).tables]
            if not table_name in table_names:
                logger.warning("table %s doesn't exist @ db with id %s" \
                               % (table_name , db_id))
                raise NoSuchEcosystem("ecosystem_id: %d" % ecosystem_id)
        cls.__tablename__ = table_name
        cls.__table__.name = table_name


class EsKeys(EsModel):
    _tablename_suffix_ = '_keys'
    __tablename__ = '1_keys'
    #__table_args__ = {'extend_existing': True}
    __bind_key__ = None

    id = db.Column(db.Integer, primary_key=True)
    pub = db.Column(db.LargeBinary)
    amount = db.Column(db.Numeric)
    multi = db.Column(db.Integer)
    delete = db.Column(db.Integer)
    block = db.Column(db.Integer)


class EsParams(EsModel):
    _tablename_suffix_ = '_parameters'
    __tablename__ = '1_parameters'
    #__table_args__ = {'extend_existing': True}
    __bind_key__ = None

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    value = db.Column(db.Text)
    conditions = db.Column(db.Text)


def get_table_object(self, core_name, es_id):
    metadata = MetaData()
    table_name = es_id + '_' + core_name
    table_object = Table(table_name, metadata,
        db.Column('id', db.Integere, primary_key=True),
        db.Column('pub', db.LargeBinary),
        db.Column('amount', db.String),
        db.Column('multi', db.Integer),
        db.Column('block', db.Integer)
    )
    mapper(EsKeys, table_object)
    return EsKeys 


class HookedColumnProperty(ColumnProperty):
    def __init__(self, *args, **kwargs):
        super(HookedColumnProperty, self).__init__(*args, **kwargs)

hooked_column_property = public_factory(HookedColumnProperty,
                                        ".orm.hooked_column_property")


class EcosystemCommon(db.Model):

    __table_args__ = {'extend_existing': True}
    __bind_key__ = None
    __abstract__ = True

    id = db.Column(db.BigInteger, primary_key=True)

    @hybrid_property
    def members_count(self):
        model = EsKeys
        model.set_ecosystem(self.id)
        q = select([func.count(model.id)]).select_from(model)
        res = db.session.execute(q).scalar()
        return res

    @hybrid_method
    def get_members_count(self, **kwargs):
        try:
            db_id = kwargs.get('db_id', 1)
            logger.debug("db_id: %d" % db_id)
            model = EsKeys
            model.set_ecosystem(self.id, db_id=db_id)
            q = select([func.count(model.id)]).select_from(model)
            session = sm.get(db_id)
            res = session.execute(q).scalar()
            return res
        except NoSuchEcosystem as e:
            logger.warning("ecosystem_id: %s" % self.id)
            return 0


def get_ecosystem_model(**kwargs):
    backend_features = kwargs.get('backend_features', None)
    if backend_features is None:
        backend_features = []
    if 'system_parameters_at_ecosystem' in backend_features:
        class Ecosystem(EcosystemCommon, EsModel):
            __tablename__ = '1_ecosystems'
            _tablename_suffix_ = '1_ecosystems'
    else:
        class Ecosystem(EcosystemCommon):
            __tablename__ = 'system_states'
    return Ecosystem


class SysParamCommon(db.Model):
    
        __bind_key__ = None
        __abstract__ = True
        __table_args__ = {'extend_existing': True}
    
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String)
        value = db.Column(db.Text)
        conditions = db.Column(db.Text)


def get_sys_param_model(**kwargs):
    backend_features = kwargs.get('backend_features', None)
    if backend_features is None:
        backend_features = []
    if 'system_parameters_at_ecosystem' in backend_features:
        class SysParam(SysParamCommon, EsModel):
            __tablename__ = '1_system_parameters'
            _tablename_suffix_ = '_system_parameters'
    else:
        class SysParam(SysParamCommon):
            __tablename__ = 'system_parameters'
    return SysParam

