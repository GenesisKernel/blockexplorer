from pprint import pprint
from datetime import datetime, timezone

from flask import render_template, request, jsonify, current_app as app
from datatables import ColumnDT, DataTables
from sqlalchemy.orm.exc import NoResultFound

from ...logging import get_logger
from ...db import db

from ...models.db_engine.model import get_model_data_by_db_id_and_table_name
from ...models.db_engine.session import SessionManager
from ...models.genesis.helpers import FullNode
from ...models.genesis.explicit import get_sys_param_model
from ...models.genesis.utils import get_by_id_or_first_genesis_db_id

from ...datatables import DataTablesExt

from ..utils import ts_to_fmt_time

from genesis_block_chain.parser.common_parse_data_full import parse_block

logger = get_logger(app)

class DataTablesSysParams(DataTablesExt):
    pass

@app.route("/genesis/database/<int:id>/sys_params_adv")
def sys_params_adv(id):
    column_names = ['Name', 'Value', 'Conditions']
    fn_column_names = ['TCP Address', 'TCP Port', 'API URL', 'Key ID',
                    'Public Key']
    valid_db_id = get_by_id_or_first_genesis_db_id(id)
    return render_template('genesis/sys_params_adv.html',
                            project=app.config.get('PRODUCT_BRAND_NAME') + ' Block Explorer',
                            db_id=id,
                            valid_db_id=valid_db_id,
                            column_names=column_names,
                            columns_num=len(column_names),
                            fn_column_names=fn_column_names,
                            fn_columns_num=len(fn_column_names))

