from flask import current_app as app

from genesis_blockchain_api_client.session import Session

from .logging import get_logger

logger = get_logger()

def get_backend_session(backend_id):
    urls = app.config.get('BACKEND_API_URLS')
    return Session(urls[backend_id])

def get_block_data(backend_id, block_id):
    sess = get_backend_session(backend_id)
    return sess.get_block_data(block_id)

def get_block(backend_id, block_id):
    sess = get_backend_session(backend_id)
    return sess.get_block(block_id)

def get_detailed_block_data(backend_id, block_id):
    sess = get_backend_session(backend_id)
    return sess.get_detailed_block_data(block_id)

def get_detailed_block(backend_id, block_id):
    sess = get_backend_session(backend_id)
    return sess.get_detailed_block(block_id)

