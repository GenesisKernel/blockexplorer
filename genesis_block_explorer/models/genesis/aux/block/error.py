import logging

from sqlalchemy.sql import func

from sqlalchemy.schema import DropTable
from sqlalchemy.ext.compiler import compiles

@compiles(DropTable, "postgresql")
def _compile_drop_table(element, compiler, **kwargs):
    return compiler.visit_drop_table(element) + " CASCADE"

from .....db import db

#from . import BlockPrevNextItemMixin

logger = logging.getLogger(__name__)

class ErrorModel(db.Model): #, BlockPrevNextItemMixin):

    __tablename__ = 'blocks_errors'

    id = db.Column(db.Integer, primary_key=True,
                   comment="Block Error Record ID")
    block_id = db.Column(db.Integer, comment="Block ID")
    created_at = db.Column(db.DateTime(timezone=True), comment="Created At",
                           server_default=func.now())
    error = db.Column(db.String, comment="Error")
    raw_error = db.Column(db.String, comment="Raw Error")

