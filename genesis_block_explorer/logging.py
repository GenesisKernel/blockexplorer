import logging
from logging.handlers import RotatingFileHandler

logging_basename = 'genesis_block_explorer'

handler = RotatingFileHandler('.'.join([logging_basename, 'log']),
                              maxBytes=10000, backupCount=1)
formatter = logging.Formatter( "%(asctime)s | %(pathname)s:%(lineno)d | %(funcName)s | %(levelname)s | %(message)s ")
level = logging.DEBUG
handler.setLevel(level)
handler.setFormatter(formatter)

def get_logger(_app=None, **kwargs):
    if _app:
        return _app.logger
    if 'app' in globals():
        return globals()['app'].logger

    else:
        return logging.getLogger(logging_basename)
