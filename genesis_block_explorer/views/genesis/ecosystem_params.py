from pprint import pprint
from datetime import datetime, timezone

from flask import render_template, request, jsonify, current_app as app
from sqlalchemy import func
from sqlalchemy.orm.exc import NoResultFound

from ...logging import get_logger
from ...db import db

from ...models.db_engine.model import get_model_data_by_db_id_and_table_name
from ...models.db_engine.session import SessionManager
from ...models.genesis.explicit import get_ecosystem_model, EsParams
from ...models.genesis.utils import get_by_id_or_first_genesis_db_id

from datatables import ColumnDT, DataTables
from ...datatables import DataTablesExt

from genesis_block_chain.parser.common_parse_data_full import parse_block

logger = get_logger(app)
sm = SessionManager(app=app)

class DataTablesEcosystemParams(DataTablesExt):
    def ecosystem_params_post_query_process(self, **kwargs):
        pass

@app.route("/genesis/database/<int:id>/ecosystem/<int:ecosystem_id>/params")
def ecosystem_params(id, ecosystem_id):
    model = get_ecosystem_model(backend_features=sm.get_be_features(id))
    es = model.query.with_session(sm.get(id)).get_or_404(ecosystem_id)
    column_names = ['Name', 'Value', 'Conditions']
    valid_db_id = get_by_id_or_first_genesis_db_id(id)
    return render_template('genesis/ecosystem_params.html', project='values',
                            ecosystem_id=es.id,
                            db_id=id,
                            valid_db_id=valid_db_id,
                            column_names=column_names,
                            columns_num=len(column_names))

@app.route('/dt/genesis/database/<int:id>/ecosystem/<int:ecosystem_id>/params')
def dt_ecosystem_params(id, ecosystem_id):
    model = get_ecosystem_model(backend_features=sm.get_be_features(id))
    es = model.query.with_session(sm.get(id)).get_or_404(ecosystem_id)
    model = EsParams
    model.set_ecosystem(ecosystem_id)
    column_ids = ['name', 'value', 'conditions']
    columns = [getattr(model, col_id) for col_id in column_ids]
    dt_columns = [ColumnDT(m) for m in columns]
    query = db.session.query(*columns).with_session(sm.get(id))
    params = request.args.to_dict()
    rowTable = DataTablesEcosystemParams(params, query, dt_columns)
    return jsonify(rowTable.output_result())
