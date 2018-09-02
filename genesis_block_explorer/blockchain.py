from genesis_blockchain_api_client.session import Session

from .logging import get_logger

logger = get_logger()

sess = Session('http://localhost:17301/api/v2')

def get_block(backend_id, block_id):
    return sess.get_block(block_id)

def get_block_data(backend_id, block_id):
    return sess.get_block_data(block_id)
