from struct import unpack 
from collections import namedtuple
from decimal import Decimal

from flask import current_app as app

import msgpack
from msgpack.exceptions import ExtraData, UnpackValueError

from genesis_block_explorer.logging import get_logger, logging

from ..helpers.objects import SimpleAttrDictPlus

from ..consts import consts
from ..consts.structs import is_struct, make_struct
from ..converter.converter import (
    decode_length_buf, bin_unmarshal, fake_bin_unmarshal
)
from ..crypto.hash import crypto_hash, crypto_hash_double
from ..utils import tx, utils

from ..parser.common import Parser, get_parser

logger = get_logger(app)
logger.setLevel(logging.DEBUG)

class Error(Exception):
    pass

class BlockParseError(Error):
    pass

class BlockHeaderParseError(BlockParseError):
    pass

class BlockTransactionParseError(BlockParseError):
    pass


class Block(SimpleAttrDictPlus):
    _default_attrs = {
        'header': utils.BlockData(),
        'prev_header': utils.BlockData(),
        'mrkl_root': None,
        'bin_data': None,
        'parser': [],
        'sys_update': False,
        'gen_block': False,
        'stop_count': -1,
    }

    def __init__(self, *args, **kwargs):
        self.update_from_default_attrs()


def parse_block_header(data):
    block_version, block_id, time, ecosystem_id, key_id_len = unpack('>hiiib', data[:15])
    key_id, = unpack('<q', data[15:15+key_id_len])
    node_position, = unpack('>b', data[15+key_id_len:15+key_id_len+1])

    offset = 0
    sign = None
    sign_bin = None
    sign_size = None
    if block_id > 1:
        logger.debug("parse_block_header offset: %d" % offset)
        sign_size, sign_size_offset  = decode_length_buf(data[15+key_id_len+1:])
        if sign_size == 0 or sign_size_offset == 0 :
            raise BlockHeaderParseError("sign_size: %s, sign_size_offset: %s" \
                    % (sign_size, sign_size_offset))
        logger.debug("parse_block_header sign_size: %d sign_size_offset: %d" % (sign_size, sign_size_offset))
        sign_bin = data[15+key_id_len+1+sign_size_offset:15+key_id_len+1+sign_size_offset + sign_size]
        sign = sign_bin.hex()
        offset = 15 + key_id_len + 1 + sign_size_offset + sign_size
    else:
        offset = 15 + key_id_len + 1 + 1

    header = utils.BlockData({
        'block_id': block_id,
        'time': time,
        'ecosystem_id': ecosystem_id,
        'key_id': key_id,
        'node_position': node_position,
        'sign': sign,
        'version': block_version,
        'extra': utils.BlockExtraData({
            'key_id_len': key_id_len,
            'offset': offset,
            'sign_size': sign_size,
            'sign_bin': sign_bin,
        })
    })
    return header

def is_contract_transaction(tx_type):
    return tx_type > 127

def parse_block(data, **kwargs):
    header = parse_block_header(data)
    offset = header['extra']['offset'] + 1
    tx_size, tx_size_offset = decode_length_buf(data[:offset]) #offset:])
    data = data[offset:]
    tx_size, tx_size_offset = decode_length_buf(data[offset:])
    tx_raw = data[offset+tx_size_offset:offset+tx_size_offset+tx_size]
    tx_info = {'size': tx_size, 'size_offset': tx_size_offset, 'raw': tx_raw}

    p = parse_transaction(tx_raw)
    p.block_data = header

    p.tx_extra = tx.Extra({
        'size': tx_size,
        'size_offset': tx_size_offset,
        'raw': tx_raw,
    })

    parsers = [p]
    if len(p.tx_full_data) > 0:
        d_hash = crypto_hash_double(p.tx_full_data)
    return p


def is_data_msgpack_unpackable(data, **kwargs):
    unp = None
    try:
        unp = msgpack.unpackb(data, raw=kwargs.get('raw', False))
    except UnpackValueError as e:
        pass
    except ExtraData as e:
        pass
    except ValueError as e:
        pass
    except TypeError as e:
        pass
    except UnicodeDecodeError as e:
        pass
    except Exception as e:
        raise e
    return unp

def find_msgpack_unpackable_data(data):
    i = 0
    j = len(data)
    packed_max_len = -1
    found = []
    for k in range(0, j):
        print("k: %d" % k)
        for m in reversed(range(0, j + 1)):
            print("m: %d" % m)
            d = data[k:m]
            if d:
                unp = is_data_msgpack_unpackable(d)
                if unp:
                    found.append((k, m, d, unp))
                    if len(d) > packed_max_len:
                        packed_max_len = len(d)

    packed_max_len_indexes = []
    cnt = 0
    for f in found:
        if len(f[2]) == packed_max_len:
            packed_max_len_indexes.append(cnt)
        cnt += 1
    return {'data': found, 'packed_max_len': packed_max_len,
            'packed_max_len_indexes': packed_max_len_indexes}

def get_from_nested_dict(src_dict, *args):
    value = src_dict
    for arg in args:
        try:
            value = value[arg]
        except TypeError as e:
            return
        except KeyError as e:
            return
    return value

def set_if_not_empty(dst_dict, key, value):
    if value is not None:
        dst_dict[key] = value
    return dst_dict

def parse_contract_transaction(p, data):
    try:
        unp = msgpack.unpackb(data, raw=False)
    except UnicodeDecodeError as e:
        unp = {}
    except ExtraData as e:
        raise e
    except Exception as e:
        raise e
    smart_tx = tx.SmartContract()
    set_if_not_empty(smart_tx, 'type',
                     get_from_nested_dict(unp, 'Header', 'Type'))
    set_if_not_empty(smart_tx, 'time',
                     get_from_nested_dict(unp, 'Header', 'Time'))
    set_if_not_empty(smart_tx, 'ecosystem_id',
                     get_from_nested_dict(unp, 'Header', 'EcosystemID'))
    set_if_not_empty(smart_tx, 'key_id',
                     get_from_nested_dict(unp, 'Header', 'KeyID'))
    set_if_not_empty(smart_tx, 'node_position',
                     get_from_nested_dict(unp, 'Header', 'NodePosition'))
    set_if_not_empty(smart_tx, 'public_key',
                     get_from_nested_dict(unp, 'Header', 'PublicKey'))
    set_if_not_empty(smart_tx, 'bin_signatures',
                     get_from_nested_dict(unp, 'Header', 'BinSignatures'))

    set_if_not_empty(smart_tx, 'token_ecosystem',
                     get_from_nested_dict(unp, 'TokenEcosystem'))
    set_if_not_empty(smart_tx, 'max_sum',
                     get_from_nested_dict(unp, 'MaxSum'))
    set_if_not_empty(smart_tx, 'pay_over',
                     get_from_nested_dict(unp, 'PayOver'))
    set_if_not_empty(smart_tx, 'signed_by',
                     get_from_nested_dict(unp, 'SignedBy'))
    set_if_not_empty(smart_tx, 'data',
                     get_from_nested_dict(unp, 'Data'))

    p.tx_ptr = None
    p.tx_smart = smart_tx

    p.tx_time = smart_tx.time
    p.tx_ecosystem_id = smart_tx.ecosystem_id
    p.ecosystem_id = p.tx_ecosystem_id
    p.tx_key_id = smart_tx.key_id
    p.data_type = int(smart_tx.type)

    ## Header
    p.tx_type = smart_tx.type
    p.tx_time = smart_tx.time
    p.tx_node_position = smart_tx.node_position
    p.public_key = smart_tx.public_key

    ## Smart Main
    p.token_ecosystem = smart_tx.token_ecosystem
    p.max_sum = smart_tx.max_sum
    p.pay_over = smart_tx.pay_over
    p.signed_by = smart_tx.signed_by
    p.data = smart_tx.data

    contract = smart_tx.get_contract_by_id(1)
    forsign = smart_tx.forsign()
    p.tx_contract = contract
    p.tx_header = smart_tx.get_header()
    p.tx_data = smart_tx.data

    return p


def parse_struct_transaction(p, data, tx_type):
    tx_parser = get_parser(p, tx_type)
    p.tx_parser = tx_parser
    p.tx_ptr = make_struct(consts.tx_types[tx_type])
    # FIX: replace with real unmarshal p.t_ptr = bin_unmarshal(data, p.tx_ptr)
    p.tx_ptr = fake_bin_unmarshal(data, p.tx_ptr, tx_type=tx_type)
    p.tx_key_id = p.tx_ptr.tx_header.key_id
    p.tx_time = p.tx_ptr.tx_header.time
    p.tx_type = tx_type
    # FIX: retrieve ecosystem_id in the right way
    #p.tx_ecosystem_id = 
    #p.validate()
    return p

def parse_regular_transaction(p, data, tx_type):
    tx_parser = get_parser(p, tx_type)
    p.tx_parser = tx_parser
    inst = fake_bin_unmarshal(data, p.tx_ptr, tx_type=None)
    p.tx_header = inst.tx_header
    p.tx_key_id = inst.tx_header.key_id
    p.tx_time = inst.tx_header.time
    p.tx_type = tx_type
    p.tx_ecosystem_id = inst.tx_header.ecosystem_id
    return p

def parse_transaction(data):
    p = Parser()
    p.tx_hash = crypto_hash(data) 
    p.tx_user_cost = Decimal(0)
    p.tx_full_data = data
    if len(data) == 0:
        raise BlockTransactionParseError("len of data: %d" % len(data))
    try:
        p.tx_type = int.from_bytes(data[0], byteorder='little')
    except TypeError as e:
        p.tx_type = data[0]
    except Exception as e:
        raise e
    if is_contract_transaction(p.tx_type):
        p.tx_binary_data = data[1:]
        p.tx_type_str = "contract"
        p = parse_contract_transaction(p, data[1:])
    elif is_struct(p.tx_type):
        p.tx_binary_data = data
        p.tx_type_str = "structure"
        p = parse_struct_transaction(p, data, p.tx_type)
    else:
        p.tx_type_str = "regular"
        p.tx_binary_data = data[1:]
    return p

