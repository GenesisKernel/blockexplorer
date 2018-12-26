from flask import current_app as app

from ...logging import get_logger
from ..decoders import decode_dt_time

logger = get_logger(app)

class DataTablesDtTimeMixin:
    def dt_time_post_query_process(self, **kwargs):
        dt_time_ids = self.prepare_col_ids(col_ids=kwargs.get('dt_time_ids'))
        if not dt_time_ids:
            logger.warning("dt_time_ids isn't set")
        logger.debug("dt_time_post_query_process dt_time_ids: %s" % dt_time_ids)

        if self.results:
            if kwargs.get('debug_mode', False) == True:
                results = []
                for row in self.results:
                    new_cols = set()
                    for col_id, val in row.items():
                        if col_id in dt_time_ids:
                            val = decode_dt_time(val)
                        new_cols.add((col_id, val))
                    results.append(dict(new_cols))
                self.results = results
            else:
                self.results = [dict((k, decode_dt_time(v)) if k in dt_time_ids else (k, v) for k, v in item.items()) for item in self.results]

