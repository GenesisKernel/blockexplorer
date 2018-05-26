from decimal import Decimal 

from ..helpers.objects import SimpleAttrDictPlus

from ..consts import consts
from ..utils import utils
from ..utils import tx

from .first_block import FirstBlockParser

class Error(Exception):
    pass

class ParserInterface:
    def init():
        raise Error()

    def validate():
        raise Error()

    def action():
        raise Error()

    def rollback():
        raise Error()

    def header():
        return tx.Header()

def get_db_transaction_model():
    return None

class Parser(SimpleAttrDictPlus):
    _default_attrs = {
        'block_data': utils.BlockData(),
        'prev_block': utils.BlockData(),

        'data_type': -1,
        'current_version': "",
        'mrkl_root': None,
        'public_keys': [],

        'tx_binary_data': None,
        'tx_full_data': None,
        'tx_hash': None,
        'tx_slice': None,
        'tx_map': None,
        'tx_ids': 0,
        'tx_ecosystem_id_str': "",
        'tx_type': -1,
        'tx_cost': -1,
        'tx_fuel': -1,
        'tx_used_cost': Decimal('-1'),
        'tx_key_id': -1,
        'tx_time': -1,
        'tx_ecosystem_id': -1,
        'tx_node_position': -1,

        'tx_ptr': None,
        'tx_data': None,
        'tx_smart': None,
        'tx_contract': tx.SmartContract(),
        'tx_header': tx.Header(),
        'tx_parser': ParserInterface(),

        'tx_extra': tx.Extra(),

    }

    def __init__(self, *args, **kwargs):
        super(Parser, self).__init__(*args, **kwargs)

    def update_from_tx_smart(self, tx_smart, **kwargs):
        print(tx_smart)
        src_keys = ['type', 'time', 'ecosystem_id', 'key_id', 'node_position',
                    'bin_signatures', 'token_ecosystem', 'max_sum', 'pay_over',
                    'signed_by', 'data']
        src_dict= {k: v if k in src_keys else None for k, v in dict(tx_smart).items()}

def get_parser(parser, tx_type):
    if tx_type == consts.TxTypeFirstBlock:
        return FirstBlockParser()
    elif tx_type == consts.TxTypeStopNetwork:
        return StopNetworkParser()
    else:
        raise Error("Uknown tx_type: %s" % tx_type)

