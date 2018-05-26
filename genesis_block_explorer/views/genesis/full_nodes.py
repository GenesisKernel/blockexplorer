from pprint import pprint
from datetime import datetime, timezone

from flask import render_template, request, jsonify, current_app as app
from datatables import ColumnDT, DataTables
from sqlalchemy.orm.exc import NoResultFound

from ...logging import get_logger
from ...db import db

from ...models.genesis.helpers import FullNode
from ...models.genesis.utils import get_by_id_or_first_genesis_db_id

from ...datatables import DataTablesExt

from genesis_block_chain.parser.common_parse_data_full import parse_block

logger = get_logger(app)

class DataTablesFullNodes(DataTablesExt):
    pass

@app.route("/genesis/database/<int:id>/full_nodes")
def full_nodes(id):
    model = FullNode
    column_names = ['TCP Address', 'TCP Port', 'API URL', 'Key ID',
                    'Public Key']
    valid_db_id = get_by_id_or_first_genesis_db_id(id)
    return render_template('genesis/full_nodes.html', project='values',
                            db_id=id,
                            valid_db_id=valid_db_id,
                            column_names=column_names,
                            columns_num=len(column_names))

@app.route('/dt/genesis/database/<int:id>/full_nodes')
def dt_full_nodes(id):
    model = FullNode
    column_ids = ['tcp_address', 'tcp_port', 'api_url', 'key_id', 'public_key']
    columns = [getattr(model, col_id) for col_id in column_ids]
    dt_columns = [ColumnDT(m) for m in columns]
    FullNode.update_from_sys_param(id)
    query = db.session.query(*columns)
    params = request.args.to_dict()
    rowTable = DataTablesFullNodes(params, query, dt_columns)
    return jsonify(rowTable.output_result())
