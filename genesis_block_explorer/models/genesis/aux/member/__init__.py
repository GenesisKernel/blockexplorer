import logging

from sqlalchemy.ext.hybrid import hybrid_method

from flask import current_app as app

from .....db import db
from .....utils import cmp_lists_to_update_first
from .....logging import get_logger
from ..utils import (
    update_dict_with_key_id, update_dict_with_hex_stringable_bytes
)
from ..generic.prev_next_item import PrevNextItemMixin

#logger = get_logger(app) 
logger = logging.getLogger(__name__)

class MemberPrevNextItemMixin(PrevNextItemMixin):
    @hybrid_method
    def get_prev_next_info(self, **kwargs):
        session = kwargs.get('session', db.session)
        has_prev = self.has_prev(session=session)
        if has_prev:
            prev_block_id = self.prev(session=session).id
        else:
            prev_block_id = 0
        has_next = self.has_next(session=session)
        if has_next:
            next_block_id = self.next(session=session).id
        else:
            next_block_id = 0
        info = {
            'has_prev': has_prev,
            'prev_block_id': prev_block_id, 
            'has_next': has_next,
            'next_block_id': next_block_id, 
        }
        return info

class Error(Exception): pass
class CompareNumError(Error): pass

class MemberModel(db.Model, MemberPrevNextItemMixin):

    CompareNumError=CompareNumError

    __tablename__ = 'members'

    id = db.Column(db.Integer, primary_key=True, comment="Member Record ID")
    ecosystem_id = db.Column(db.Integer, comment="Ecosystem ID")
    key_id = db.Column(db.Integer, comment="Raw Key ID")
    ukey_id = db.Column(db.String, comment="Key ID")
    pub = db.Column(db.String, comment="Public Key")
    amount = db.Column(db.Numeric, comment="Amount")
    maxpay = db.Column(db.Numeric, comment="Max Pay")
    multi = db.Column(db.Integer, comment="Multi Signature")
    deleted = db.Column(db.Integer, comment="Deleted")
    blocked = db.Column(db.Integer, comment="Blocked")


    @hybrid_method
    def to_dict(self, style='common'):
        d = {
            'id': self.id,
            'ecosystem_id': self.ecosystem_id,
            'key_id': self.key_id,
            'ukey_id': self.ukey_id,
            'pub': self.pub,
            'amount': self.amount,
            'maxpay': self.maxpay,
            'multi': self.multi,
            'deleted': self.deleted,
            'blocked': self.blocked,
        }
        return d

    @classmethod
    def prepare_dict(cls, data, **kwargs):
        data = update_dict_with_key_id(data)
        data = update_dict_with_hex_stringable_bytes(data, names=['pub'])
        ecosystem_id= kwargs.get('ecosystem_id')
        if ecosystem_id:
            data['ecosystem_id'] = ecosystem_id
        return data

    @classmethod
    def add_record_from_dict(cls, data, **kwargs):
        session = kwargs.get('session', db.session)
        member = cls(**data)
        session.add(member)
        if kwargs.get('db_session_commit_enabled', True):
            session.commit()

    @classmethod
    def add_record_from_model_instance(cls, instance, **kwargs):
        session = kwargs.get('session', db.session)
        ecosystem_id = kwargs.get('ecosystem_id', instance.get_ecosystem())
        data = cls.prepare_dict(instance.to_dict(id_field_name='key_id'),
                                ecosystem_id=ecosystem_id)
        cls.add_record_from_dict(data, session=session,
                                 db_session_commit_enabled=kwargs.get(
                                    'db_session_commit_enabled', True))

    @classmethod
    def add_all_records_from_model(cls, model, **kwargs):
        session = kwargs.get('session', db.session)
        m_session = kwargs.get('model_session')
        ecosystem_id = kwargs.get('ecosystem_id', model.get_ecosystem())
        for item in m_session.query(model).all():
            logger.debug("item: %s" % item)
            cls.add_record_from_model_instance(item, session=session,
                                               db_session_commit_enabled=False)
        if kwargs.get('db_session_commit_enabled', True):
            session.commit()

    @classmethod
    def add_all_records_for_all_ecosystems(cls, model, **kwargs):
        session = kwargs.get('session', db.session)
        m_session = kwargs.get('model_session')
        es_model = kwargs.get('ecosystem_model')
        for es in m_session.query(es_model).all():
            model.set_ecosystem(es.id)
            cls.add_all_records_from_model(model, session=session,
                                           model_session=m_session,
                                           ecosystem_id=es.id,
                                           db_session_commit_enabled=False)
        if kwargs.get('db_session_commit_enabled', True):
            session.commit()

    @classmethod
    def compare_num_of_all_records_for_all_ecosystems(cls, model, **kwargs):
        session = kwargs.get('session', db.session)
        m_session = kwargs.get('model_session')
        es_model = kwargs.get('ecosystem_model')
        total = 0
        for es in m_session.query(es_model).all():
            model.set_ecosystem(es.id)
            total += m_session.query(model).count()
        cnt = session.query(cls).count()
        if cnt != total:
            raise cls.CompareNumError("EsKeys side: %d MemberModel side: %d" \
                    % (total, cnt))

    @classmethod
    def update_all_records_for_all_ecosystems(cls, model, **kwargs):
        dryrun = kwargs.get('dryrun', False)
        session = kwargs.get('session', db.session)
        m_session = kwargs.get('model_session')
        es_model = kwargs.get('ecosystem_model')
        src_es_ids = []
        for es in m_session.query(es_model).all():
            model.set_ecosystem(es.id)
            ids_orig = [i[0] for i in m_session.query(model.id).all()]
            ids_repl = [i[0] for i in session.query(cls.key_id).filter_by(ecosystem_id=es.id).all()]
            res = cmp_lists_to_update_first(ids_repl, ids_orig)
            if res['to_add']:
                for m_item in m_session.query(model).filter(model.id.in_(res['to_add'])).all():
                    cls.add_record_from_model_instance(m_item, session=session,
                                               db_session_commit_enabled=False)
            if res['to_delete']:
                for item in session.query(cls).filter(cls.key_id.in_(res['to_delete'])).all():
                    session.delete(item)
        if kwargs.get('db_session_commit_enabled', True):
            session.commit()

