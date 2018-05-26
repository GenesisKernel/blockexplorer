from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from sqlalchemy import func

from ...db import db
from ...logging import get_logger
from ...debug_utils import (
    get_function_name as _fn,
    get_function_name2 as _fn2,
    get_function_parameters_and_values as _fpav,
    get_class_name_of_function as _cnof,
    get_class_and_function_names as _cafn,
    get_function_name_and_parameters_and_values as _fnapav,
    get_class_and_function_names_and_parameters_and_values as _cafnapav,
)

logger = get_logger()

class InfoBlockMixin(object):
    @hybrid_property
    def hash_hex(self):
        return self.hash.hex()

    @hash_hex.expression
    def hash_hex(cls):
        return cls.hash.hex()

class BlockChainMixin2(object):
    @property
    def hash_hex(self):
        return self.hash.hex()

block_chain_mixin_decorators_map = [
    ['hash_hex', 'hybrid_propety'],
    ['hash_hex', 'hash_hex.expression'],
]

class BlockChainMixin(object):
    @property
    def hash_hex(self):
        return self.hash.hex()

from sqlalchemy import Column
from sqlalchemy.types import LargeBinary
class BlockChainMixin2(object):
    hash = Column('hash', LargeBinary())
    __tablename__ = 'block_chain'
    @hybrid_property
    def hash_hex2(self):
        return self.hash.hex()

    @hash_hex2.expression
    def hash_hex2(cls):
        return cls.hash.hex()


