from ..utils import ts_to_fmt_time, dt_to_fmt_time

def decode_hash(val):
    return val.hex()

def decode_data(val):
    try:
        val = val.decode('utf8')
    except UnicodeDecodeError:
        try:
            val = val.decode('raw_unicode_escape')
        except UnicodeDecodeError:
            val = str(val)
    return val

def decode_time(val, utc=False):
    return ts_to_fmt_time(val, utc=utc)

def decode_dt_time(val, utc=False):
    return dt_to_fmt_time(val, utc=utc)

