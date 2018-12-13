from pprint import pprint
from datetime import datetime, timezone

from flask import render_template, request, jsonify, current_app as app
from datatables import ColumnDT, DataTables
from sqlalchemy.orm.exc import NoResultFound

from ....logging import get_logger
from ....db import db
from ....models.genesis.aux.session import AuxSessionManager
from ....models.genesis.aux.tx import TxModel
from ....models.genesis.utils import get_by_id_or_first_genesis_db_id
from ....models.genesis.aux.utils import get_valid_seq_num

from ....datatables import DataTablesExt

from .common import ColumnManager

logger = get_logger(app)
asm = AuxSessionManager(app=app)
colman = ColumnManager(TxModel, drop_column_ids=['id'])

class DataTablesBlocks(DataTablesExt):
    pass

@app.route("/genesis/backend/<int:seq_num>/transactions")
def aux_transactions(seq_num):
    column_names = colman.titles
    #seq_num = get_valid_seq_num(seq_num, app=app)
    seq_num = get_by_id_or_first_genesis_db_id(seq_num)
    return render_template('genesis/aux/transactions.html',
                            project=app.config.get('PRODUCT_NAME'),
                            seq_num=seq_num,
                            valid_db_id=seq_num,
                            socketio_namespace='/backend%d' % seq_num,
                            column_names=column_names,
                            columns_num=len(column_names))

@app.route('/dt/genesis/backend/<int:seq_num>/transactions')
def dt_aux_transactions(seq_num):
    columns = colman.columns
    dt_columns = colman.dt_columns
    query = db.session.query(*columns).with_session(asm.get(seq_num))
    params = request.args.to_dict()
    rowTable = DataTablesBlocks(params, query, dt_columns)
    return jsonify(rowTable.output_result())

