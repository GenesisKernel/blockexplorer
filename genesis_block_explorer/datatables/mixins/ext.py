import six

from flask import current_app as app

from ...utils import is_number
from ...logging import get_logger

logger = get_logger(app)

class DataTablesExtMixin:
    def prepare_col_ids(self, **kwargs):
        col_ids = kwargs.get('col_ids')
        if not col_ids:
            return [] 
        try:
            iter(col_ids)
        except TypeError as e:
            col_ids = [col_ids]
        except Exception as e:
            raise e

        _col_ids = []
        for col_id in col_ids:
            if is_number(col_id):
                col_id = str(col_id)
            elif isinstance(col_id, six.string_types):
                pass
            else:
                raise TypeError("col_ids element can me number or string")
            _col_ids.append(col_id)
        logger.debug("prepare_col_ids col_ids: %s _col_ids: %s" \
                     % (col_ids, _col_ids))
        return _col_ids

    def post_query_process(self, **kwargs):
        logger.debug("post_query_process kwargs: %s" % kwargs)
        col_ids = self.prepare_col_ids(**kwargs)
        if not col_ids:
            logger.warning("col_ids isn't set")
            return
        caller = kwargs.get('caller')
        if not caller:
            logger.warning("caller isn't set")
            return
        caller_args = kwargs.get('caller_args', [])
        caller_kwargs = kwargs.get('caller_kwargs', {})
        call_as = kwargs.get('call_as', 'func')
        allowed_callers = kwargs.get('allowed_callers', {
            'str': str,
            'hex': hex,
        })

        if self.results:
            if kwargs.get('debug_mode', False) == True:
                results = []
                for row in self.results:
                    logger.debug("type(row): %s, row: %s" % (type(row), row))
                    new_cols = set()
                    for col_id, val in row.items():
                        if col_id in col_ids:
                            if call_as == 'func':
                                _caller_args = [val] + caller_args
                                val = caller(*_caller_args, **caller_kwargs)
                            elif call_as == 'func_name':
                                _caller_args = [val] + caller_args
                                val = allowed_callers[caller](*_caller_args,
                                                            **caller_kwargs)
                            elif call_as == 'meth':
                                _caller_args = []
                                val = getattr(val, caller)(*_caller_args,
                                                           **caller_kwargs)
                        new_cols.add((col_id, val))
                    results.append(dict(new_cols))
                self.results = results
            else:
                if call_as == 'func':
                    self.results = [dict((k, caller(v)) if k in col_ids else (k, v) for k, v in item.items()) for item in self.results]
                elif call_as == 'func_name':
                    self.results = [dict((k, allowed_callers[caller](v)) if k in col_ids else (k, v) for k, v in item.items()) for item in self.results]
                elif call_as == 'meth':
                    self.results = [dict((k, getattr(v, caller)() ) if k in col_ids else (k, v) for k, v in item.items()) for item in self.results]

    def post_query_jsonify(self, **kwargs):
        if self.results:
            pass

    def post_query_multi_process(self, proc_list=[]):
        # TODO: make it processing
        pass
