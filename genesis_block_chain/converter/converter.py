from typing import Iterable, List, Set, Callable
from struct import unpack

from flask import current_app as app

from genesis_block_explorer.logging import get_logger, logging

from ..consts import fake

logger = get_logger(app)
logger.setLevel(logging.DEBUG)

class Error(Exception):
    pass

def decode_length_buf(data: bytes):
    if len(data) == 0:
        logger.error("decode_len_buf len(data) = 0")
        return 0, 0
    offset = 1
    logger.error("decode_len_buf data[:offset]: %s" % str(data[:offset]))
    length = int.from_bytes(data[:offset], byteorder='little')
    logger.error("decode_len_buf length: %d" % length)
    
    if length & 0x80 == 0:
        logger.error("decode_len_buf length & 0x80 == 0, length: %d" % length)
        return length, offset
    logger.error("decode_len_buf 2) length: %d" % length)

    length &= 0x7f
    logger.error("decode_len_buf 3) length: %d" % length)
    if len(data) < length:
        raise Error("data length: %d, length: %d" % (len(data), length))
    return length, offset

def fake_bin_unmarshal(data, obj, tx_type=None):
    logger.error("fake_bin_unmarshal data: %s obj: %s" % (data, obj))
    return fake.create_fake_instance(tx_type)

def bin_unmarshal(data, obj):
    logger.error("bin_unmarshal data: %s obj: %s" % (data, obj))



