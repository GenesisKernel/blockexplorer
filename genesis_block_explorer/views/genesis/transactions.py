from pprint import pprint
from datetime import datetime, timezone

from flask import render_template, request, jsonify, current_app as app
from datatables import ColumnDT, DataTables
from sqlalchemy.orm.exc import NoResultFound

from ...logging import get_logger
from ...db import db

from ...models.db_engine.model import get_model_data_by_db_id_and_table_name
from ...models.db_engine.session import SessionManager
from ...models.genesis.explicit import TransactionsStatus
from ...models.genesis.utils import get_by_id_or_first_genesis_db_id

from ...datatables import DataTablesExt

from ..utils import ts_to_fmt_time

from genesis_block_chain.parser.common_parse_data_full import parse_block

logger = get_logger(app)
sm = SessionManager(app=app)

class DataTablesTransactions(DataTablesExt):
    def transactions_post_query_process(self, **kwargs):
        logger.debug("transactions_post_query_processkwargs: %s" % kwargs)
        hash_ids = self.prepare_col_ids(col_ids=kwargs.get('hash_ids'))
        if not hash_ids:
            logger.warning("hash_ids isn't set")
        logger.debug("transactions_post_query_process hash_ids: %s" % hash_ids)

        time_ids = self.prepare_col_ids(col_ids=kwargs.get('time_ids'))
        if not time_ids:
            logger.warning("time_ids isn't set")
        logger.debug("transactions_post_query_process time_ids: %s" % time_ids)

        if self.results:
            if kwargs.get('debug_mode', False) == True:
                results = []
                for row in self.results:
                    #logger.debug("type(row): %s, row: %s" % (type(row), row))
                    new_cols = set()
                    for col_id, val in row.items():
                        if col_id in hash_ids:
                            val = val.hex()
                        if col_id in time_ids:
                            val = ts_to_fmt_time(val, utc=False)
                        new_cols.add((col_id, val))
                    results.append(dict(new_cols))
                self.results = results
            else:
                raise Exception("Not implemented yet")
                #self.results = [dict((k, v.hex()) if k in hash_ids else (k, v) for k, v in item.items()) for item in self.results]
                #self.results = [dict((k, ts_to_fmt_time(v, utc=False)) if k in time_ids else (k, v) for k, v in item.items()) for item in self.results]

@app.route("/genesis/database/<int:id>/transactions")
def transactions(id):
    table, model, model_name \
            = get_model_data_by_db_id_and_table_name(id, 'block_chain')
    columns = model.__table__.columns
    column_names = ['Time', 'Sender Key ID', 'Ecosystem ID',
                    'Block ID', 'Hash', 'Type', 'Error']
    valid_db_id = get_by_id_or_first_genesis_db_id(id)
    return render_template('genesis/transactions.html', project='values',
                            table_id=table.id, table_name=table.name,
                            db_id=table.database.id,
                            valid_db_id=valid_db_id,
                            db_name=table.database.name,
                            db_bind_name=table.database.bind_name,
                            model_name=model.__name__,
                            hash_col_ind=4, block_id_col_ind=3,
                            column_names=column_names,
                            columns_num=len(column_names))

@app.route('/dt/genesis/database/<int:id>/transactions')
def dt_transactions(id):
    model = TransactionsStatus
    column_ids = ['time', 'wallet_id', 'ecosystem',
                  'block_id', 'hash', 'type', 'error']
    columns = [getattr(model, col_id) for col_id in column_ids]
    dt_columns = [ColumnDT(m) for m in columns]
    query = db.session.query(*columns).with_session(sm.get(id))
    params = request.args.to_dict()
    rowTable = DataTablesTransactions(params, query, dt_columns)
    rowTable.transactions_post_query_process(hash_ids=4, time_ids=[0],
                                             debug_mode=True)
    return jsonify(rowTable.output_result())
