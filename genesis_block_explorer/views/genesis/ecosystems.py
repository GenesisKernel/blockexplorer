from pprint import pprint
from datetime import datetime, timezone

from flask import render_template, request, jsonify, current_app as app
from sqlalchemy import func
from sqlalchemy.orm.exc import NoResultFound

from ...logging import get_logger
from ...db import db

from ...models.db_engine.model import get_model_data_by_db_id_and_table_name
from ...models.db_engine.session import SessionManager
from ...models.genesis.explicit import get_ecosystem_model, EsKeys
from ...models.genesis.utils import get_by_id_or_first_genesis_db_id

from datatables import ColumnDT, DataTables
from ...datatables import DataTablesExt

from genesis_block_chain.parser.common_parse_data_full import parse_block

logger = get_logger(app)
sm = SessionManager(app=app)

class DataTablesEcosystems(DataTablesExt):
    def ecosystem_post_query_process(self, **kwargs):
        logger.debug("ecosystems_post_query_process kwargs: %s" % kwargs)
        
        id_ids = self.prepare_col_ids(
                            col_ids=kwargs.get('id_ids'))
        if not id_ids:
            logger.warning("id_ids isn't set")
        logger.debug("ecosystems_post_query_process id_ids : %s" % id_ids)

        members_count_ids = self.prepare_col_ids(
                            col_ids=kwargs.get('members_count_ids'))
        if not members_count_ids:
            logger.warning("members_count_ids isn't set")
        logger.debug("ecosystems_post_query_process members_count_ids : %s" % members_count_ids)

        db_id = kwargs.get('db_id', 1)
        model = get_ecosystem_model(backend_features=sm.get_be_features(db_id))
        logger.debug("db_id: %d" % db_id)
        if self.results:
            if kwargs.get('debug_mode', False) == True:
                results = []
                for row in self.results:
                    new_cols = set()
                    rec_id = row[id_ids[0]]
                    logger.debug("ecosystems_post_query_process rec_id: %s db_id: %s" % (rec_id, db_id))
                    mc = model.query.with_session(sm.get(db_id)).get(rec_id).get_members_count(db_id=db_id)
                    for col_id, val in row.items():
                        if col_id in members_count_ids:
                            val = mc
                        new_cols.add((col_id, val))
                    results.append(dict(new_cols))
                self.results = results
            else:
                self.results = [dict((k, v.hex()) if k in members_count_ids else (k, v) for k, v in item.items()) for item in self.results]

@app.route("/genesis/database/<int:id>/ecosystems")
def ecosystems(id):
    column_names = ['ID', 'Members']
    valid_db_id = get_by_id_or_first_genesis_db_id(id)
    return render_template('genesis/ecosystems.html',
                            project=app.config.get('PRODUCT_BRAND_NAME') + ' Block Explorer',
                            db_id=id,
                            valid_db_id=valid_db_id,
                            column_names=column_names,
                            columns_num=len(column_names))

@app.route('/dt/genesis/database/<int:id>/ecosystems')
def dt_ecosystems(id):
    model = get_ecosystem_model(backend_features=sm.get_be_features(id))
    column_ids = ['id', 'id']
    columns = [getattr(model, col_id) for col_id in column_ids]
    columns = [model.id, model.id]
    dt_columns = [ColumnDT(m) for m in columns]
    logger.debug("id: %d sm.get: %s" % (id, sm.get(id)))
    query = db.session.query(*columns).with_session(sm.get(id))
    params = request.args.to_dict()
    rowTable = DataTablesEcosystems(params, query, dt_columns)
    rowTable.ecosystem_post_query_process(db_id=id,
                                          id_ids=[0],
                                          members_count_ids=1,
                                          debug_mode=True)
    return jsonify(rowTable.output_result())
