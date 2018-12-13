from ...utils import is_number
from .engine import check_db_engine_discovery_map

class Error(Exception):
    pass

class WrongDbSeqNumError(Error):
    pass

def get_valid_seq_num(app, seq_num, **kwargs):
    db_engine_discovery_map_name = kwargs.get('db_engine_discovery_map_name',
                                              'DB_ENGINE_DISCOVERY_MAP')
    check_db_engine_discovery_map(app,
        db_engine_discovery_map_name=db_engine_discovery_map_name)
    db_engine_discovery_map = app.config.get(db_engine_discovery_map_name)
    if not is_number(seq_num):
        raise WrongDbSeqNumError("'%s' provided as database sequence number, but shoud be a number >= 1 nad <= %d" % (seq_num, len(db_engine_discovery_map)))
    seq_num = int(seq_num)
    if seq_num < 1 or seq_num > len(db_engine_discovery_map):
        raise WrongDbSeqNumError("'%s' provided as database sequence number, but shoud be a number >= 1 and <= %d" % (seq_num, len(db_engine_discovery_map)))
    return seq_num

