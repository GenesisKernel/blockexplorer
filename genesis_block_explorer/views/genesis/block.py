from pprint import pprint
from datetime import datetime, timezone

from flask import request
from flask import render_template, request, jsonify, current_app as app

from datatables import ColumnDT, DataTables
from sqlalchemy.orm.exc import NoResultFound

from ...logging import get_logger
from ...db import db

from ...models.genesis.helpers import BlockHelper 
from ...models.genesis.utils import get_by_id_or_first_genesis_db_id

from ...datatables import DataTablesExt

logger = get_logger(app)

class DataTablesBlockHelper(DataTablesExt):
    pass

@app.route("/genesis/database/<int:id>/block/<int:block_id>")
def block(id, block_id):
    show_raw_data = bool(request.args.get("show_raw_data", False))
    model = BlockHelper 
    column_names = ['Title', 'Value']
    valid_db_id = get_by_id_or_first_genesis_db_id(id)
    return render_template('genesis/block.html',
                            project=app.config.get('PRODUCT_BRAND_NAME') + ' Block Explorer',
                            db_id=id,
                            valid_db_id=valid_db_id,
                            block_id=block_id,
                            show_raw_data=show_raw_data,
                            column_names=column_names,
                            columns_num=len(column_names))

@app.route('/dt/genesis/database/<int:id>/block/<int:block_id>')
def dt_block(id, block_id):
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
