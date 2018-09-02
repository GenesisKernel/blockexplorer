from pprint import pprint

from flask import render_template, request, jsonify, current_app as app
from datatables import ColumnDT, DataTables
from sqlalchemy.orm.exc import NoResultFound

from ...logging import get_logger
from ...db import db
from ...models.db_engine.model import (
    get_model_data_by_table_id, automapped_classes
)
from ...models.genesis.utils import get_by_id_or_first_genesis_db_id
from ...datatables import (
    DataTablesExt,
    DataTablesHash,
    DataTablesTime,
    DataTablesHashData,
    DataTablesHashDataTime,
    DataTablesHashTime,
)

logger = get_logger(app)

@app.route("/db-engine/table/<int:id>/values")
def values(id):
    table, model, model_name = get_model_data_by_table_id(id)
    column_names = model.__table__.columns.keys()
    valid_db_id = get_by_id_or_first_genesis_db_id(id)
    return render_template('db_engine/values.html',
                            project=app.config.get('PRODUCT_BRAND_NAME') + ' Block Explorer',
                            table_id=table.id, table_name=table.name,
                            db_id=table.database.id,
                            valid_db_id=valid_db_id,
                            db_name=table.database.name,
                            db_bind_name=table.database.bind_name,
                            model_name=model.__name__,
                            column_names=column_names,
                            columns_num=len(column_names))

@app.route('/dt/db-engine/table/<int:id>/values')
def dt_values(id):
    table, model, model_name = get_model_data_by_table_id(id)
    columns = model.__table__.columns

    dt_columns = [ColumnDT(getattr(model, cn)) for cn in columns.keys()]
    t = (getattr(model, cn) for cn in columns.keys())
    query = db.session.query(*t) 
    params = request.args.to_dict()
    logger.debug("table.name: %s" % table.name)
    if table.name == 'log_transactions' or table.name == 'transactions_status':
        rowTable = DataTablesHashTime(params, query, dt_columns)
        rowTable.hash_time_post_query_process(hash_ids=[0], time_ids=1,
                                             debug_mode=True)
    elif table.name == 'info_block':
        rowTable = DataTablesHashTime(params, query, dt_columns)
        rowTable.hash_time_post_query_process(hash_ids=[0], time_ids=5,
                                             debug_mode=True)
    elif table.name == 'transactions':
        rowTable = DataTablesHashData(params, query, dt_columns)
        rowTable.hash_data_post_query_process(hash_ids=[0], data_ids=1,
                                             debug_mode=True)
    elif table.name == 'rollback_tx':
        rowTable = DataTablesHash(params, query, dt_columns)
        rowTable.hash_post_query_process(hash_ids=[2], debug_mode=True)
    elif table.name == 'block_chain':
        rowTable = DataTablesHashDataTime(params, query, dt_columns)
        rowTable.hash_data_time_post_query_process(hash_ids=[1,2], data_ids=3,
                                                   time_ids=7, debug_mode=True)
    elif table.name == 'queue_tx' or table.name == 'queue_block':
        rowTable = DataTablesHash(params, query, dt_columns)
        rowTable.hash_post_query_process(hash_ids=[0], debug_mode=True)
    elif table.name == 'my_node_keys':
        rowTable = DataTablesTime(params, query, dt_columns)
        rowTable.time_post_query_process(time_ids=6, debug_mode=True)
    else:
        rowTable = DataTablesExt(params, query, dt_columns)
    return jsonify(rowTable.output_result())
