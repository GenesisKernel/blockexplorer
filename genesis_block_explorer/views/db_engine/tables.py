from pprint import pprint

from flask import render_template, request, jsonify, current_app as app
from datatables import ColumnDT, DataTables

from ...logging import get_logger
from ...models.db_engine.database import db, Database, Table
from ...models.genesis.utils import get_by_id_or_first_genesis_db_id

from ...datatables import DataTablesExt

logger = get_logger(app)

@app.route("/db-engine/database/<int:id>/tables")
def tables(id):
    database = Database.query.get(id)
    valid_db_id = get_by_id_or_first_genesis_db_id(id)
    column_names = ['ID', 'Name', 'Values/Columns']
    return render_template('db_engine/tables.html', project='tables',
                            valid_db_id=valid_db_id,
                            db_name=database.name, db_id=database.id,
                            columns_values_ind=2,
                            column_names=column_names,
                            columns_num=len(column_names))

@app.route('/dt/db-engine/database/<int:id>/tables')
def dt_tables(id):
    model = Table 
    column_ids = ['id', 'name', 'name']
    columns = [getattr(model, col_id) for col_id in column_ids]
    dt_columns = [ColumnDT(m) for m in columns]
    query = db.session.query(*columns).filter_by(database_id=id)
    params = request.args.to_dict()
    rowTable = DataTablesExt(params, query, dt_columns)
    return jsonify(rowTable.output_result())
