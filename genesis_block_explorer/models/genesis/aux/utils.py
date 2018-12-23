import datetime

from flask import current_app as app

from genesis_blockchain_tools.convert.genesis import key_id_to_wallet

from ....logging import get_logger

logger = get_logger(app)

def get_valid_seq_num(seq_num, **kwargs):
    app  = kwargs.get('app')
    map_name = kwargs.get('db_engine_discovery_map_name',
                          'DB_ENGINE_DISCOVERY_MAP')

    aux_map_name = kwargs.get('aux_db_engine_discovery_map_name',
                              'AUX_DB_ENGINE_DISCOVERY_MAP')

    #print("get_valid_seq_num() source seq_num: %s" % seq_num)
    if not app.config.get(aux_map_name) \
    or seq_num not in range(1, len(app.config.get(aux_map_name)) + 1):
        seq_num = 0
    #print("get_valid_seq_num() final seq_num: %s" % seq_num)
    return seq_num

def update_dict_with_key_id(data, **kwargs):
    key_id_to_str = kwargs.get('key_id_to_str', True)
    src_key_id_name = kwargs.get('src_key_id_name', 'key_id')
    dst_key_id_name = kwargs.get('dst_key_id_name', src_key_id_name)
    if src_key_id_name in data:
        key_id = data[src_key_id_name]
    else:
        key_id = 0
    if key_id:
        data['wallet'] = key_id_to_wallet(key_id)
    else:
        data['wallet'] = '0'
    if src_key_id_name != dst_key_id_name:
        del data[src_key_id_name]
    if key_id_to_str:
        data[dst_key_id_name] = str(key_id)
    else:
        data[dst_key_id_name] = key_id
    #print("update_dict_with_key_id 1 data: %s" % data)
    return data

def ts_time_to_dt_time(ts_time):
    if app and hasattr(app, 'config') and app.config.get('TIME_FORMAT'):
        fmt = app.config.get('TIME_FORMAT')
    else:
        fmt = '%d/%b/%Y %H:%M:%S'
    return datetime.datetime.fromtimestamp(ts_time).strftime(fmt)

def ts_time_to_dtu_time(ts_time):
    if app and hasattr(app, 'config') and app.config.get('TIME_FORMAT'):
        fmt = app.config.get('TIME_FORMAT')
    else:
        fmt = '%d/%b/%Y %H:%M:%S'
    return datetime.datetime.utcfromtimestamp(ts_time).strftime(fmt)

def update_dict_with_time(data):
    if 'time' in data:
        try:
            ts_time = int(data.pop('time'))
        except TypeError:
            logger.info("time value is None")
            ts_time = 0
    else:
        ts_time = 0
    data['time_ts'] = ts_time
    data['time_dt'] = ts_time_to_dt_time(ts_time)
    data['time_dtu'] = ts_time_to_dtu_time(ts_time)
    return data

def update_dict_with_hex_stringable_bytes(data, **kwargs):
    names = kwargs.get('names', [])
    for name in names:
        if name in data:
            data[name] = data[name].hex()
    return data
        

