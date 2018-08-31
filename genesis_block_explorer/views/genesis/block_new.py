from pprint import pprint
from datetime import datetime, timezone

from flask import request
from flask import render_template, request, jsonify, current_app as app

from ...logging import get_logger
from datatables import ColumnDT, DataTables
from sqlalchemy.orm.exc import NoResultFound

from ...db import db

from ...models.genesis.explicit import BlockChain
from ...models.genesis.helpers import BlockHelper 
from ...models.db_engine.session import SessionManager
from ...models.genesis.utils import get_by_id_or_first_genesis_db_id

from ...datatables import DataTablesExt

logger = get_logger(app)
sm = SessionManager(app=app)

class DataTablesBlockHelper(DataTablesExt):
    pass

@app.route("/genesis/database/<int:id>/block_new/<int:block_id>")
def block_new(id, block_id):
    show_raw_data = bool(request.args.get("show_raw_data", False))
    model = BlockHelper 
    block = BlockChain.query.with_session(sm.get(id)).get(block_id)
    has_prev = block.has_prev(db_id=id)
    if has_prev:
        prev_block_id = block.prev(db_id=id).id
    else:
        prev_block_id = 0
    has_next = block.has_next(db_id=id)
    if has_next:
        next_block_id = block.next(db_id=id).id
    else:
        next_block_id = 0
    column_names = ['Title', 'Value']
    t_column_names = ['Time', 'Sender Key ID', 'Ecosystem ID',
                    'Hash', 'Type', 'Error']
    valid_db_id = get_by_id_or_first_genesis_db_id(id)
    return render_template('genesis/block_new.html',
                            project=app.config.get('PRODUCT_BRAND_NAME') + ' Block Explorer',
                            db_id=id,
                            block_id=block_id,
                            block=block,
                            has_prev=has_prev,
                            has_next=has_next,
                            prev_block_id=prev_block_id,
                            next_block_id=next_block_id,
                            show_raw_data=show_raw_data,
                            column_names=column_names,
                            columns_num=len(column_names),
                            valid_db_id=valid_db_id,
                            hash_col_ind=3,
                            t_column_names=t_column_names,
                            t_columns_num=len(t_column_names))

@app.route('/dt/genesis/database/<int:id>/block-data/<int:block_id>')
def block_data(id, block_id):
    show_raw_data = request.args.get("show_raw_data", False)
    if show_raw_data == "False":
        show_raw_data = False
    model = BlockHelper 
    column_ids = ['title', 'value']
    columns = [getattr(model, col_id) for col_id in column_ids]
    dt_columns = [ColumnDT(m) for m in columns]
    BlockHelper.update_from_block_chain(db_id=id, block_id=block_id,                                                    show_raw_data=show_raw_data)
    query = db.session.query(*columns).filter_by(db_id=id, block_id=block_id)
    params = request.args.to_dict()
    rowTable = DataTablesBlockHelper(params, query, dt_columns)
    return jsonify(rowTable.output_result())
