from pprint import pprint

from flask import render_template, request, jsonify, current_app as app
from datatables import ColumnDT, DataTables

from ...logging import get_logger
from ...models.db_engine.database import db, Database, Table, get_logger
from ...datatables import DataTablesExt
from ...models.genesis.utils import get_by_id_or_first_genesis_db_id

logger = get_logger(app)

@app.route("/db-engine/databases")
def databases():
    valid_db_id = get_by_id_or_first_genesis_db_id()
    column_names = ['ID', 'Name', 'Engine', 'Driver', 'Backend Version']
    return render_template('db_engine/databases.html',
                            project=app.config.get('PRODUCT_BRAND_NAME') + ' Block Explorer',
                            valid_db_id=valid_db_id,
                            column_names=column_names,
                            columns_num=len(column_names))

@app.route('/dt/db-engine/databases')
def dt_databases():
    model = Database
    column_ids = ['id', 'name', 'engine', 'driver', 'backend_version']
    columns = [getattr(model, col_id) for col_id in column_ids]
    dt_columns = [ColumnDT(m) for m in columns]
    query = db.session.query(*columns).filter(Database.name!=':memory:')
    params = request.args.to_dict()
    rowTable = DataTablesExt(params, query, dt_columns)
    return jsonify(rowTable.output_result())

