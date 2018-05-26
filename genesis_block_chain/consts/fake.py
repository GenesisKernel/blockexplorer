from datetime import datetime, timezone
from random import randint

from .consts import (
    TxTypeFirstBlock,
    TxTypeStopNetwork,
)

from .structs import (
    TxHeader,
    FirstBlock,
    StopNetwork,
)

class Error(Exception):
    pass

def create_fake_instance(tx_type):
    tx_header = TxHeader(type=tx_type,
                         time=datetime.now(timezone.utc).timestamp(),
                         key_id=randint(111111111, 999999999)
                        )
    if tx_type == TxTypeFirstBlock:
        return FirstBlock(tx_header=tx_header,
                          public_key = randint(111111111, 999999999),
                          node_public_key = randint(111111111, 999999999),
                          stop_network_cert_bundle = randint(111111, 999999)
                         )
    elif tx_type == TxTypeStopNetwork:
        return StopNetwork(tx_header=tx_header, 
                           stop_network_cert_bundle = randint(111111, 999999)
                          )
    else:
        raise Error("Unknown tx_type: %s" % tx_type)

