import re

try:
    from urlparse import urlparse
except:
    from urllib.parse import urlparse

from flask import request, current_app as app

from ..logging import get_logger

logger = get_logger(app)

def get_db_id_from_request():
    logger.debug("request.url: %s" % request.url)
    logger.debug("request.query_string: %s" % request.query_string)
    db_id = None
    if request and hasattr(request, 'url'):
        p = urlparse(request.url)
        logger.debug("path: %s" % p.path)
        m = re.search('^\/(genesis|db-engine)\/database\/([0-9]+)\/.*', p.path)
        logger.debug("m: %s" % m)
        if m:
            try:
                db_id = int(m.group(2))
            except Exception as e:
                pass
    return db_id
