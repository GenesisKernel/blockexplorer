from pprint import pprint
from datetime import datetime, timezone

from flask import render_template, request, jsonify, current_app as app
from datatables import ColumnDT, DataTables
from sqlalchemy.orm.exc import NoResultFound

from ...logging import get_logger
from ...db import db

from ...models.db_engine.model import get_model_data_by_db_id_and_table_name
from ...models.db_engine.session import SessionManager
from ...models.genesis.explicit import BlockChain 
from ...models.genesis.utils import get_by_id_or_first_genesis_db_id

from ...datatables import DataTablesExt

from genesis_block_chain.parser.common_parse_data_full import (
        parse_block, ExtraData, UnpackValueError
)
from genesis_block_chain.parser.common import Parser

logger = get_logger(app)
sm = SessionManager(app=app)

class DataTablesBlocks(DataTablesExt):
    def blocks_post_query_process(self, **kwargs):
        logger.debug("blocks_post_query_process kwargs: %s" % kwargs)
        hash_ids = self.prepare_col_ids(col_ids=kwargs.get('hash_ids'))
        if not hash_ids:
            logger.warning("hash_ids isn't set")
        logger.debug("blocks_post_query_process hash_ids: %s" % hash_ids)

        time_ids = self.prepare_col_ids(col_ids=kwargs.get('time_ids'))
        if not time_ids:
            logger.warning("time_ids isn't set")
        logger.debug("blocks_post_query_process time_ids: %s" % time_ids)

        data_ids = self.prepare_col_ids(col_ids=kwargs.get('data_ids'))
        if not data_ids:
            logger.warning("data_ids isn't set")
        logger.debug("blocks_post_query_process data_ids: %s" % data_ids)

        eco_ids = self.prepare_col_ids(col_ids=kwargs.get('eco_ids'))
        if not eco_ids:
            logger.warning("eco_ids isn't set")
        logger.debug("blocks_post_query_process eco_ids: %s" % eco_ids)

        if self.results:
            if kwargs.get('debug_mode', False) == True:
                results = []
                for row in self.results:
                    #logger.debug("type(row): %s, row: %s" % (type(row), row))
                    new_cols = set()
                    p_data = dict()
                    for col_id, val in row.items():
                        if col_id in hash_ids:
                            val = val.hex()
                        if col_id in time_ids:
                            val = ts_to_fmt_time(val, utc=False)
                        if col_id in data_ids:
                            parse_error = False
                            try:
                                logger.error("val: %s" % val)
                                p = parse_block(val)
                            except ExtraData as e:
                                parse_error = True
                            except UnpackValueError as e:
                                parse_error = True
                            except Exception as e:
                                msg = "Parse Block Error, row: %s; error: %s" \
                                        % (row, e)
                                logger.error(msg)
                                raise e

                            if parse_error:
                                p_data['key_id'] = ''
                            else:
                                if hasattr(p, 'block_data'):
                                    if 'key_id' in p.block_data:
                                        p_data['key_id'] = \
                                            p.block_data['key_id']
                                    if 'ecosystem_id' in p.block_data:
                                        p_data['ecosystem_id'] = \
                                            p.block_data['ecosystem_id']
                                if hasattr(p, 'ecosystem_id'):
                                    p_data['ecosystem_id'] = \
                                            p.ecosystem_id
                                if hasattr(p, 'tx_smart') \
                                and p.tx_smart \
                                and 'ecosystem_id' in p.tx_smart:
                                    p_data['ecosystem_id'] = \
                                            p.tx_smart['ecosystem_id']
                                if hasattr(p, 'key_id'):
                                    p_data['key_id'] = \
                                        p['key_id']

                        new_cols.add((col_id, val))
                    new_cols2 = set()
                    for col_id, val in new_cols:
                        if col_id in eco_ids and 'ecosystem_id' in p_data:
                            val = p_data['ecosystem_id']
                        if col_id in data_ids and 'key_id' in p_data:
                            val = p_data['key_id']
                        new_cols2.add((col_id, val))
                    results.append(dict(new_cols2))
                self.results = results
            else:
                raise Exception("Not implemented yet")
                #self.results = [dict((k, v.hex()) if k in hash_ids else (k, v) for k, v in item.items()) for item in self.results]
                #self.results = [dict((k, ts_to_fmt_time(v, utc=False)) if k in time_ids else (k, v) for k, v in item.items()) for item in self.results]

@app.route("/genesis/database/<int:id>/blocks_adv")
def blocks_adv(id):
    table, model, model_name \
            = get_model_data_by_db_id_and_table_name(id, 'block_chain')
    columns = model.__table__.columns
    column_names = ['Block ID', 'Time', 'Hash', 'Node Position', 'Ecosystem ID',
            'Key ID', 'TX']
    t_column_names = ['Time', 'Sender Key ID', 'Ecosystem ID',
                    'Block ID', 'Hash', 'Type', 'Error']
    valid_db_id = get_by_id_or_first_genesis_db_id(id)
    return render_template('genesis/blocks_adv.html',
                            project=app.config.get('PRODUCT_BRAND_NAME') + ' Block Explorer',
                            table_id=table.id, table_name=table.name,
                            db_id=table.database.id,
                            db_name=table.database.name,
                            db_bind_name=table.database.bind_name,
                            model_name=model.__name__,
                            tx_col_ind=6, block_id_col_ind=0,
                            valid_db_id=valid_db_id,
                            column_names=column_names,
                            columns_num=len(column_names),
                            t_hash_col_ind=4, t_block_id_col_ind=3,
                            t_column_names=t_column_names,
                            t_columns_num=len(t_column_names))
