from pprint import pprint
from datetime import datetime, timezone

from flask import render_template, request, jsonify, current_app as app
from sqlalchemy import func
from sqlalchemy.orm.exc import NoResultFound

from ...logging import get_logger
from ...db import db

from ...models.db_engine.model import get_model_data_by_db_id_and_table_name
from ...models.db_engine.session import SessionManager
from ...models.genesis.explicit import get_ecosystem_model, get_keys_model
from ...models.genesis.utils import get_by_id_or_first_genesis_db_id

from datatables import ColumnDT, DataTables
from ...datatables import DataTablesExt

from genesis_block_chain.parser.common_parse_data_full import parse_block

logger = get_logger(app)
sm = SessionManager(app=app)

class DataTablesEcosystemMembers(DataTablesExt):
    def ecosystem_members_post_query_process(self, **kwargs):
        logger.debug("ecosystems_post_query_process kwargs: %s" % kwargs)

        key_ids = self.prepare_col_ids(
                            col_ids=kwargs.get('key_ids'))
        if not key_ids:
            logger.warning("key_ids isn't set")
        logger.debug("ecosystems_post_query_process avatar_ids : %s" % key_ids)
        
        avatar_ids = self.prepare_col_ids(
                            col_ids=kwargs.get('avatar_ids'))
        if not avatar_ids:
            logger.warning("avatar_ids isn't set")
        logger.debug("ecosystems_post_query_process avatar_ids : %s" % avatar_ids)
        decimal_ids = self.prepare_col_ids(
                            col_ids=kwargs.get('decimal_ids'))
        if not decimal_ids:
            logger.warning("decimal_ids isn't set")
        logger.debug("ecosystems_post_query_process decimal_ids : %s" % decimal_ids)
        public_key_ids = self.prepare_col_ids(
                            col_ids=kwargs.get('public_key_ids'))
        if not public_key_ids:
            logger.warning("public_key_ids isn't set")
        logger.debug("ecosystems_post_query_process public_key_ids : %s" % public_key_ids)
        if self.results:
            if kwargs.get('debug_mode', False) == True:
                results = []
                for row in self.results:
                    new_cols = set()
                    for col_id, val in row.items():
                        if col_id in avatar_ids:
                            pass
                        if col_id in key_ids:
                            val = str(val)
                        if col_id in decimal_ids:
                            val = str(val)
                        if col_id in public_key_ids:
                            val = val.hex()
                        new_cols.add((col_id, val))
                    results.append(dict(new_cols))
                self.results = results
            else:
                raise Exception("Not implemented yet")
                #self.results = [dict((k, v) if k in avatar_ids else (k, v) for k, v in item.items()) for item in self.results]

@app.route("/genesis/database/<int:id>/ecosystem/<int:ecosystem_id>/members")
def ecosystem_members(id, ecosystem_id):
    es_model = get_ecosystem_model(backend_features=sm.get_be_features(id))
    es = es_model.query.with_session(sm.get(id)).get_or_404(ecosystem_id)
    column_names = ['Key ID', 'Amount', 'Public Key']
    valid_db_id = get_by_id_or_first_genesis_db_id(id)
    return render_template('genesis/ecosystem_members.html',
                            project=app.config.get('PRODUCT_BRAND_NAME') + ' Block Explorer',
                            ecosystem_id=es.id,
                            db_id=id,
                            valid_db_id=valid_db_id,
                            column_names=column_names,
                            columns_num=len(column_names))

@app.route('/dt/genesis/database/<int:id>/ecosystem/<int:ecosystem_id>/members')
def dt_ecosystem_members(id, ecosystem_id):
    es_model = get_ecosystem_model(backend_features=sm.get_be_features(id))
    es = es_model.query.with_session(sm.get(id)).get_or_404(ecosystem_id)
    model = get_keys_model(backend_features=sm.get_be_features(id))
    model.set_ecosystem(ecosystem_id)
    column_ids = ['id', 'amount', 'pub']
    columns = [getattr(model, col_id) for col_id in column_ids]
    dt_columns = [ColumnDT(m) for m in columns]
    query = db.session.query(*columns).with_session(sm.get(id))
    params = request.args.to_dict()
    rowTable = DataTablesEcosystemMembers(params, query, dt_columns)
    rowTable.ecosystem_members_post_query_process(db_id=id,
                                          key_ids=[0],
                                          decimal_ids=1,
                                          public_key_ids=2,
                                          avatar_ids=[0],
                                          debug_mode=True)
    return jsonify(rowTable.output_result())
