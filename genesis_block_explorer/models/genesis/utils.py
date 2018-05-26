from flask import current_app as app

from ...logging import get_logger
from ..db_engine.database import Database

logger = get_logger(app)

def get_first_db():
    return Database.query.first()

def get_by_id_or_first_db(id):
    return Database.query.first()

def get_first_genesis_db():
    return Database.query.first()

def get_by_id_or_first_genesis_db(*args):
    logger.debug("args: %s" % str(args))
    find_first = False
    if len(args) == 0:
        find_first = True 
    else:
        db_id = args[0]
        db = Database.query.get(db_id)
        if db:
            return db
        else:
            find_first = True 
    if find_first:
        return Database.query.first()

def get_by_id_or_first_genesis_db_id(*args):
    default_id = 1
    if len(args) >= 2:
        default_id = args[1]
    db = get_by_id_or_first_genesis_db(*args)
    if db:
        return db.id
    else:
        return default_id

