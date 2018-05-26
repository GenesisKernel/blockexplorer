from pprint import pprint

from flask import render_template, request, jsonify, current_app as app
from datatables import ColumnDT, DataTables

from ...logging import get_logger
from ...models.db_engine.column import Column, db
from ...models.db_engine.model import (
    get_model_data_by_table_id, automapped_classes
)
from ...models.genesis.utils import get_by_id_or_first_genesis_db_id
from ...datatables import DataTablesExt

logger = get_logger(app)

@app.route("/db-engine/table/<int:id>/columns")
def columns(id):
    table, model, model_name = get_model_data_by_table_id(id)
    column_names = ['Name', 'Type', 'Default', 'AutoIncrement',
                  'Primary Key']
    valid_db_id = get_by_id_or_first_genesis_db_id(id)
    return render_template('db_engine/columns.html', project='values',
                            table_id=table.id, table_name=table.name,
                            valid_db_id=valid_db_id,
                            db_id=table.database.id,
                            db_name=table.database.name,
                            db_bind_name=table.database.bind_name,
                            model_name=model.__name__,
                            column_names=column_names,
                            columns_num=len(column_names))

@app.route('/dt/db-engine/table/<int:id>/columns')
def dt_columns(id):
    model = Column
    column_ids = ['name', 'type', 'default', 'autoincrement',
                  'primary_key']
    columns = [getattr(model, col_id) for col_id in column_ids]
    dt_columns = [ColumnDT(m) for m in columns]
    query = db.session.query(*columns).filter_by(table_id=id)
    params = request.args.to_dict()
    rowTable = DataTablesExt(params, query, dt_columns)
    return jsonify(rowTable.output_result())
