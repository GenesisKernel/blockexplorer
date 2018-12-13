import enum
import os
from datetime import timedelta, datetime

from sqlalchemy import Enum, func, and_

from flask import current_app as app

from ....process import check_pid
from ....db import db
from ....logging import get_logger

logger = get_logger(app) 

class Error(Exception):
    pass

class LockModel(db.Model):

    __tablename__ = 'locks'

    id = db.Column(db.Integer, primary_key=True)
    context = db.Column(db.String, default='default_context')
    process_id = db.Column(db.Integer, default=os.getpid())
    created_at = db.Column(db.DateTime, default=func.now())

    @classmethod
    def is_locked(cls, **kwargs):
        context = kwargs.get('context', 'default_context')
        session = kwargs.get('session', db.session)
        return len(cls.query.with_session(session=session).filter_by(context=context).all()) > 0

    @classmethod
    def lock(cls, **kwargs):
        context = kwargs.get('context', 'default_context')
        session = kwargs.get('session', db.session)
        process_id = kwargs.get('process_id', os.getpid())
        l = cls(context=context, process_id=process_id)
        session.add(l)
        session.commit()

    @classmethod
    def unlock(cls, **kwargs):
        context = kwargs.get('context', 'default_context')
        session = kwargs.get('session', db.session)
        qs = cls.query.with_session(session).filter_by(context=context).all()
        if qs:
            [session.delete(q) for q in qs]
            session.commit()

    @classmethod
    def get_latest_lock(cls, **kwargs):
        context = kwargs.get('context', 'default_context')
        session = kwargs.get('session', db.session)
        qs = session.query(cls, func.max(cls.created_at).label("value")).filter_by(context=context).all()
        if qs and qs[0] and qs[0][0]:
            return qs[0][0]

    @classmethod
    def get_zombie_locks(cls, **kwargs):
        context = kwargs.get('context', 'default_context')
        session = kwargs.get('session', db.session)
        qs = session.query(cls).filter_by(context=context).all()
        return [q for q in qs if not check_pid(q.process_id)]

    @classmethod
    def delete_zombie_locks(cls, **kwargs):
        context = kwargs.get('context', 'default_context')
        session = kwargs.get('session', db.session)
        qs = cls.get_zombie_locks(context=context, session=session)
        if qs:
            [session.delete(q) for q in qs]
            session.commit()

    @classmethod
    def get_expired_locks(cls, **kwargs):
        timeout_secs = kwargs.get('timeout_secs', 30)
        context = kwargs.get('context', 'default_context')
        session = kwargs.get('session', db.session)
        return session.query(cls).filter(and_(context==context,
            LockModel.created_at < \
                    datetime.utcnow() - timedelta(seconds=timeout_secs)
        )).all()

    @classmethod
    def delete_expired_locks(cls, **kwargs):
        timeout_secs = kwargs.get('timeout_secs', 30)
        context = kwargs.get('context', 'default_context')
        session = kwargs.get('session', db.session)
        qs = cls.get_expired_locks(session=session, context=context,
                                   timeout_secs=timeout_secs)
        if qs:
            [session.delete(q) for q in qs]
            session.commit()

    @classmethod
    def clear_garbage(cls, **kwargs):
        timeout_secs = kwargs.get('timeout_secs', 30)
        context = kwargs.get('context', 'default_context')
        session = kwargs.get('session', db.session)
        cls.delete_zombie_locks(context=context, session=session)
        cls.delete_expired_locks(context=context, session=session,
                                 timeout_secs=timeout_secs)

