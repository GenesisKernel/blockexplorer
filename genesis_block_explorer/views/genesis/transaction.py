from pprint import pprint
from datetime import datetime, timezone

from flask import request
from flask import render_template, request, jsonify, current_app as app

from datatables import ColumnDT, DataTables
from sqlalchemy.orm.exc import NoResultFound

from ...logging import get_logger
from ...db import db

from ...models.genesis.helpers import TransactionHelper 
from ...models.genesis.utils import get_by_id_or_first_genesis_db_id

from ...datatables import DataTablesExt

from ..utils import ts_to_fmt_time

logger = get_logger(app)
#sm = SessionManager(app=app)

class DataTablesTransactionHelper(DataTablesExt):
    pass

@app.route("/genesis/database/<int:id>/transaction/<string:tx_hash>")
def transaction(id, tx_hash):
    show_raw_data = bool(request.args.get("show_raw_data", False))
    model = TransactionHelper 
    #column_names = ['Name', 'Title', 'Source', 'Raw', 'Type', 'Value']
    column_names = ['Title', 'Value']
    valid_db_id = get_by_id_or_first_genesis_db_id(id)
    return render_template('genesis/transaction.html', project='values',
                            db_id=id,
                            valid_db_id=valid_db_id,
                            tx_hash=tx_hash,
                            show_raw_data=show_raw_data,
                            column_names=column_names,
                            columns_num=len(column_names))

@app.route('/dt/genesis/database/<int:id>/transaction/<string:tx_hash>')
def dt_transaction(id, tx_hash):
    show_raw_data = request.args.get("show_raw_data", False)
    if show_raw_data == "False":
        show_raw_data = False
    model = TransactionHelper 
    #column_ids = ['name', 'title', 'src', 'raw', 'type', 'value']
    column_ids = ['title', 'value']
    columns = [getattr(model, col_id) for col_id in column_ids]
    dt_columns = [ColumnDT(m) for m in columns]
    TransactionHelper.update_from_transactions_status(db_id=id, tx_hash=tx_hash)
    query = db.session.query(*columns).filter_by(db_id=id, tx_hash=tx_hash)
    params = request.args.to_dict()
    rowTable = DataTablesTransactionHelper(params, query, dt_columns)
    return jsonify(rowTable.output_result())
