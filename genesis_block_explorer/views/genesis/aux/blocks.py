from pprint import pprint
from datetime import datetime, timezone

from flask import render_template, request, jsonify, current_app as app
#from datatables import ColumnDT, DataTables
from sqlalchemy.orm.exc import NoResultFound

from ....logging import get_logger
from ....db import db
from ....models.genesis.aux.session import AuxSessionManager
from ....models.genesis.aux.block import BlockModel
from ....models.genesis.aux.utils import get_valid_seq_num
from ....models.genesis.utils import get_by_id_or_first_genesis_db_id
from ....datatables import (
    DataTablesExt,
    DataTablesDtTime,
)

from .common import ColumnManager

logger = get_logger(app)
asm = AuxSessionManager(app=app)
colman = ColumnManager(BlockModel, drop_column_ids=['header_id'])

class DataTablesBlocks(DataTablesExt): pass
#class DataTablesBlocks(DataTablesDtTime): pass

def get_async_mode():
    return "dummy"

@app.route("/genesis/backend/<int:seq_num>/blocks")
def aux_blocks(seq_num):
    column_names = colman.titles
    #seq_num = get_valid_seq_num(seq_num, app=app)
    seq_num = get_by_id_or_first_genesis_db_id(seq_num)
    return render_template('genesis/aux/blocks.html',
                            project=app.config.get('PRODUCT_NAME'),
                            valid_db_id=seq_num,
                            seq_num=seq_num,
                            socketio_namespace='/backend%d' % seq_num,
                            async_mode=get_async_mode(),
                            column_names=column_names,
                            columns_num=len(column_names))

@app.route('/dt/genesis/backend/<int:seq_num>/blocks')
def dt_aux_blocks(seq_num):
    columns = colman.columns
    dt_columns = colman.dt_columns
    query = db.session.query(*columns).with_session(asm.get(seq_num))
    params = request.args.to_dict()
    rowTable = DataTablesBlocks(params, query, dt_columns)
    #rowTable = DataTablesDtTime(params, query, dt_columns)
    #rowTable.dt_time_post_query_process(dt_time_ids=1, debug_mode=True)
    return jsonify(rowTable.output_result())
