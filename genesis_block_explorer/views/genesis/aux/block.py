from pprint import pprint
from datetime import datetime, timezone

from flask import render_template, request, jsonify, current_app as app
from flask import jsonify, url_for
#from datatables import ColumnDT, DataTables
from sqlalchemy.orm.exc import NoResultFound

from ....logging import get_logger
from ....db import db
from ....models.genesis.aux.session import AuxSessionManager
from ....models.genesis.aux.block import BlockModel
from ....models.genesis.aux.block.header import HeaderModel
from ....models.genesis.aux.block.error import ErrorModel
from ....models.genesis.aux.block.error.helper import ErrorHelperModel
from ....models.genesis.aux.tx import TxModel
from ....models.genesis.aux.block.helper import (
    BlockHelperModel, BlockHelperManager
)
from ....models.genesis.aux.block.header.helper import (
    HeaderHelperModel, HeaderHelperManager
)
from ....models.genesis.aux.block.error.helper import (
    ErrorHelperModel, ErrorHelperManager
)
from ....models.genesis.aux.utils import get_valid_seq_num
from ....models.genesis.utils import get_by_id_or_first_genesis_db_id
from ....datatables import DataTablesExt

from .common import ColumnManager
from ....models.genesis.aux.engine import get_aux_helpers_engine
from ....models.genesis.aux.session import get_aux_helpers_session

logger = get_logger(app)
asm = AuxSessionManager(app=app)

colman_tm = ColumnManager(TxModel, drop_column_ids=['id', 'block_id'])
colman_hm = ColumnManager(HeaderModel, drop_column_ids=[])
#colman_em = ColumnManager(ErrorModel, drop_column_ids=[])

colman_bhm = ColumnManager(BlockHelperModel,
                           drop_column_ids=['id', 'seq_num', 'block_id'])

colman_hhm = ColumnManager(HeaderHelperModel,
                           drop_column_ids=['id', 'seq_num', 'block_id'])

colman_ehm = ColumnManager(ErrorHelperModel,
                           drop_column_ids=['id', 'block_id', 'name'])

class DataTablesBlocks(DataTablesExt):
    pass

def get_block_prev_next_info(seq_num, block_id):
    session = asm.get(seq_num)
    block = session.query(BlockModel).get(block_id)
    info = block.get_prev_next_info(session=session)
    info['prev_block_url'] = url_for('aux_block', seq_num=seq_num,
                                     block_id=info['prev_block_id'])
    info['next_block_url'] = url_for('aux_block', seq_num=seq_num,
                                     block_id=info['next_block_id'])
    return info

@app.route("/genesis/backend/<int:seq_num>/block/<int:block_id>")
def aux_block(seq_num, block_id):
    column_names = colman_bhm.titles
    h_column_names = colman_hhm.titles
    t_column_names = colman_tm.titles
    #seq_num = get_valid_seq_num(seq_num, app=app)
    seq_num = get_by_id_or_first_genesis_db_id(seq_num)
    pn_info = get_block_prev_next_info(seq_num, block_id)
    bm_instance = BlockModel.query.with_session(asm.get(seq_num)).filter_by(id=block_id).one()
    error = False
    if bm_instance.error:
        error = True
        column_names = colman_ehm.titles
    return render_template('genesis/aux/block.html',
                            project=app.config.get('PRODUCT_NAME'),
                            seq_num=seq_num,
                            valid_db_id=seq_num,
                            socketio_namespace='/backend%d' % seq_num,
                            block_id=block_id,
                            column_names=column_names,
                            columns_num=len(column_names),
                            has_prev=pn_info['has_prev'],
                            has_next=pn_info['has_next'],
                            prev_block_id=pn_info['prev_block_id'],
                            next_block_id=pn_info['next_block_id'],
                            h_column_names=h_column_names,
                            h_columns_num=len(h_column_names),
                            t_column_names=t_column_names,
                            t_columns_num=len(t_column_names),
                            error=error)

@app.route("/genesis/backend/<int:seq_num>/block/<int:block_id>/prev_next_info")
def aux_block_prev_next_info(seq_num, block_id):
    return jsonify(get_block_prev_next_info(seq_num, block_id))

@app.route('/dt/genesis/backend/<int:seq_num>/block/<int:block_id>/helper')
def dt_aux_block_helper(seq_num, block_id):
    bhm_columns = colman_bhm.columns
    bhm_dt_columns = colman_bhm.dt_columns
    bm_instance = BlockModel.query.with_session(asm.get(seq_num)).filter_by(id=block_id).one()
    bhm = BlockHelperManager(app=app, engine_echo=True)
    bhm.model.update_from_main_model_instance(bm_instance,
        session=bhm.session, main_model_session=asm.get(seq_num))
    query = bhm.session.query(*bhm_columns)
    params = request.args.to_dict()
    rowTable = DataTablesBlocks(params, query, bhm_dt_columns)
    return jsonify(rowTable.output_result())

@app.route('/dt/genesis/backend/<int:seq_num>/block/<int:block_id>/header/helper')
def dt_aux_block_header_helper(seq_num, block_id):
    hhm_columns = colman_hhm.columns
    hhm_dt_columns = colman_hhm.dt_columns
    hm_instance = BlockModel.query.with_session(asm.get(seq_num)).filter_by(id=block_id).one().header
    hhm = HeaderHelperManager(app=app, engine_echo=True)
    hhm.model.update_from_main_model_instance(hm_instance,
        session=hhm.session, main_model_session=asm.get(seq_num))
    query = hhm.session.query(*hhm_columns)
    params = request.args.to_dict()
    rowTable = DataTablesBlocks(params, query, hhm_dt_columns)
    return jsonify(rowTable.output_result())

@app.route('/dt/genesis/backend/<int:seq_num>/block/<int:block_id>/error/helper')
def dt_aux_block_error_helper(seq_num, block_id):
    ehm_columns = colman_ehm.columns
    ehm_dt_columns = colman_ehm.dt_columns
    em_instance = BlockModel.query.with_session(asm.get(seq_num)).filter_by(id=block_id).one().error
    ehm = ErrorHelperManager(app=app, engine_echo=True)
    ehm.model.update_from_main_model_instance(em_instance,
        session=ehm.session, main_model_session=asm.get(seq_num))
    query = ehm.session.query(*ehm_columns)
    params = request.args.to_dict()
    rowTable = DataTablesBlocks(params, query, ehm_dt_columns)
    return jsonify(rowTable.output_result())

@app.route('/dt/genesis/backend/<int:seq_num>/block/<int:block_id>/transactions/helper')
def dt_aux_block_transactions_helper(seq_num, block_id):
    tm_columns = colman_tm.columns
    tm_dt_columns = colman_tm.dt_columns
    session = asm.get(seq_num)
    query = session.query(*tm_columns).filter_by(block_id=block_id)
    params = request.args.to_dict()
    rowTable = DataTablesBlocks(params, query, tm_dt_columns)
    return jsonify(rowTable.output_result())

