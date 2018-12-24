import logging

from sqlalchemy.sql import func

from sqlalchemy.schema import DropTable
from sqlalchemy.ext.compiler import compiles

@compiles(DropTable, "postgresql")
def _compile_drop_table(element, compiler, **kwargs):
    return compiler.visit_drop_table(element) + " CASCADE"

from .....db import db

from . import BlockPrevNextItemMixin, get_req_models

logger = logging.getLogger(__name__)
get_req_models()

class BadBlockModel(db.Model, BlockPrevNextItemMixin):

    __tablename__ = 'bad_blocks'

    id = db.Column(db.Integer, primary_key=True, comment="Block ID")
    created_at = db.Column(db.DateTime(timezone=True), comment="Created At",
                        server_default=func.now())
    raw_error = db.Column(db.String, comment="Raw Error")
    error = db.Column(db.String, comment="Error")

    @classmethod
    def add(cls, block_id, **kwargs):
        session = kwargs.get('session', db.session)
        data = {
            'id': block_id,
            'error': kwargs.get('error'),
            'raw_error': kwargs.get('raw_error'),
        }
        bb = cls(**data)
        session.add(bb)
        if kwargs.get('db_session_commit_enabled', True):
            session.commit()
        return bb
