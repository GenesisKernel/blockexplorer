from flask import current_app as app

from ...logging import get_logger
from ..decoders import decode_time

logger = get_logger(app)

class DataTablesTimeMixin:
    def time_post_query_process(self, **kwargs):
        time_ids = self.prepare_col_ids(col_ids=kwargs.get('time_ids'))
        if not time_ids:
            logger.warning("time_ids isn't set")
        logger.debug("time_post_query_process time_ids: %s" % time_ids)

        if self.results:
            if kwargs.get('debug_mode', False) == True:
                results = []
                for row in self.results:
                    #logger.debug("type(row): %s, row: %s" % (type(row), row))
                    new_cols = set()
                    for col_id, val in row.items():
                        if col_id in time_ids:
                            val = decode_time(val)
                        new_cols.add((col_id, val))
                    results.append(dict(new_cols))
                self.results = results
            else:
                raise Exception("Not implemented yet")
                #self.results = [dict((k, v.hex()) if k in hash_ids else (k, v) for k, v in item.items()) for item in self.results]
                #self.results = [dict((k, ts_to_fmt_time(v, utc=False)) if k in time_ids else (k, v) for k, v in item.items()) for item in self.results]

