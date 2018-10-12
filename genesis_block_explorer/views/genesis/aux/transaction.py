from pprint import pprint
from datetime import datetime, timezone

from flask import render_template, request, jsonify, current_app as app
from flask import url_for
from werkzeug.routing import BaseConverter
#from datatables import ColumnDT, DataTables
from sqlalchemy.orm.exc import NoResultFound

from ....logging import get_logger
from ....db import db
from ....models.genesis.aux.session import AuxSessionManager
from ....models.genesis.aux.tx import TxModel
from ....models.genesis.aux.tx.param import ParamModel
from ....models.genesis.aux.tx.helper import (
    TxHelperModel, TxHelperManager
)
from ....models.genesis.aux.utils import get_valid_seq_num
from ....models.genesis.utils import get_by_id_or_first_genesis_db_id
from ....datatables import DataTablesExt

from .common import ColumnManager
from ....models.genesis.aux.engine import get_aux_helpers_engine
from ....models.genesis.aux.session import get_aux_helpers_session

logger = get_logger(app)
asm = AuxSessionManager(app=app)

colman_pm = ColumnManager(ParamModel, drop_column_ids=['id', 'tx_id'])

colman_thm = ColumnManager(TxHelperModel,
                           drop_column_ids=['id', 'seq_num', 'hash'])

class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]
app.url_map.converters['regex'] = RegexConverter

def get_tx_prev_next_info(seq_num, tx_hash):
    session = asm.get(seq_num)
    tx = session.query(TxModel).filter_by(hash=tx_hash).one()
    info = tx.get_prev_next_info(session=session)
    info['prev_block_url'] = url_for('aux_transaction', seq_num=seq_num,
                                     tx_hash=info['prev_tx_hash'])
    info['next_block_url'] = url_for('aux_transaction', seq_num=seq_num,
                                     tx_hash=info['next_tx_hash'])
    return info

class DataTablesBlocks(DataTablesExt):
    pass

@app.route('/genesis/backend/<int:seq_num>/transaction/<regex("[a-fA-F0-9]{32,512}"):tx_hash>')
def aux_transaction(seq_num, tx_hash):
    column_names = colman_thm.titles
    p_column_names = colman_pm.titles
    #seq_num = get_valid_seq_num(seq_num, app=app)
    seq_num = get_by_id_or_first_genesis_db_id(seq_num)
    pn_info = get_tx_prev_next_info(seq_num, tx_hash)
    return render_template('genesis/aux/transaction.html',
                            project=app.config.get('PRODUCT_NAME'),
                            seq_num=seq_num,
                            valid_db_id=seq_num,
                            tx_hash=tx_hash,
                            socketio_namespace='/backend%d' % seq_num,
                            has_prev=pn_info['has_prev'],
                            has_next=pn_info['has_next'],
                            prev_tx_hash=pn_info['prev_tx_hash'],
                            next_tx_hash=pn_info['next_tx_hash'],
                            column_names=column_names,
                            columns_num=len(column_names),
                            p_column_names=p_column_names,
                            p_columns_num=len(p_column_names))

@app.route('/genesis/backend/<int:seq_num>/transaction/<regex("[a-fA-F0-9]{32,512}"):tx_hash>/prev_next_info')
def aux_transaction_prev_next_info(seq_num, tx_hash):
    return jsonify(get_tx_prev_next_info(seq_num, tx_hash))

@app.route('/dt/genesis/backend/<int:seq_num>/transaction/<regex("[a-fA-F0-9]{32,512}"):tx_hash>/helper')
def dt_aux_transaction_helper(seq_num, tx_hash):
    thm_columns = colman_thm.columns
    thm_dt_columns = colman_thm.dt_columns
    tm_instance = TxModel.query.with_session(asm.get(seq_num)).filter_by(hash=tx_hash).one()
    thm = TxHelperManager(app=app, engine_echo=True)
    thm.model.update_from_main_model_instance(tm_instance,
        session=thm.session, main_model_session=asm.get(seq_num))
    query = thm.session.query(*thm_columns)
    params = request.args.to_dict()
    rowTable = DataTablesBlocks(params, query, thm_dt_columns)
    return jsonify(rowTable.output_result())

@app.route('/dt/genesis/backend/<int:seq_num>/transaction/<regex("[a-fA-F0-9]{32,512}"):tx_hash>/parameters')
def dt_aux_transaction_parameters(seq_num, tx_hash):
    pm_columns = colman_pm.columns
    pm_dt_columns = colman_pm.dt_columns
    session = asm.get(seq_num)
    tm_instance = TxModel.query.with_session(asm.get(seq_num)).filter_by(hash=tx_hash).one()
    query = session.query(*pm_columns).filter_by(tx_id=tm_instance.id)
    params = request.args.to_dict()
    rowTable = DataTablesBlocks(params, query, pm_dt_columns)
    return jsonify(rowTable.output_result())

