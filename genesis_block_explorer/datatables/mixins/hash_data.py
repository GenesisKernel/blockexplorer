from flask import current_app as app

from ...logging import get_logger
from ..decoders import decode_hash, decode_data, decode_time

logger = get_logger(app)

class DataTablesHashDataMixin:
    def hash_data_post_query_process(self, **kwargs):
        logger.debug("hash_data_post_query_processkwargs: %s" % kwargs)
        hash_ids = self.prepare_col_ids(col_ids=kwargs.get('hash_ids'))
        if not hash_ids:
            logger.warning("hash_ids isn't set")
        logger.debug("hash_data_post_query_process hash_ids: %s" % hash_ids)

        data_ids = self.prepare_col_ids(col_ids=kwargs.get('data_ids'))
        if not data_ids:
            logger.warning("data_ids isn't set")
        logger.debug("hash_data_post_query_process data_ids: %s" % data_ids)

        if self.results:
            if kwargs.get('debug_mode', False) == True:
                results = []
                for row in self.results:
                    #logger.debug("type(row): %s, row: %s" % (type(row), row))
                    new_cols = set()
                    for col_id, val in row.items():
                        if col_id in hash_ids:
                            val = decode_hash(val)
                        if col_id in data_ids:
                            val = decode_data(val)
                        new_cols.add((col_id, val))
                    results.append(dict(new_cols))
                self.results = results
            else:
                raise Exception("Not implemented yet")
                #self.results = [dict((k, v.hex()) if k in hash_ids else (k, v) for k, v in item.items()) for item in self.results]
                #self.results = [dict((k, ts_to_fmt_time(v, utc=False)) if k in data_ids else (k, v) for k, v in item.items()) for item in self.results]

