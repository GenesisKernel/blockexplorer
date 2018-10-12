from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from sqlalchemy import func, desc

from flask import current_app as app

from .....db import db
from .....logging import get_logger

logger = get_logger(app) 

class PrevNextItemMixin:
    @hybrid_method
    def next(self, **kwargs):
        session = kwargs.get('session', db.session)
        model = self.__class__
        return model.query.with_session(session).filter(model.id > self.id).order_by(model.id).first()

    @hybrid_method
    def has_next(self, **kwargs):
        if self.next(**kwargs):
            return True
        else:
            return False

    @hybrid_method
    def prev(self, **kwargs):
        session = kwargs.get('session', db.session)
        model = self.__class__
        return model.query.with_session(session).filter(model.id < self.id).order_by(desc(model.id)).first()

    @hybrid_method
    def has_prev(self, **kwargs):
        if self.prev(**kwargs):
            return True
        else:
            return False

    @hybrid_method
    def get_prev_next_info(self, **kwargs):
        session = kwargs.get('session', db.session)
        has_prev = self.has_prev(session=session)
        has_next = self.has_next(session=session)
        info = {
            'has_prev': has_prev,
            'has_next': has_next,
        }
        return info

