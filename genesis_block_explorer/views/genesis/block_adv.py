from pprint import pprint
from datetime import datetime, timezone

from flask import request
from flask import render_template, request, jsonify, current_app as app

from ...logging import get_logger
from datatables import ColumnDT, DataTables
from sqlalchemy.orm.exc import NoResultFound

from ...db import db

from ...models.genesis.explicit import BlockChain
from ...models.genesis.helpers import BlockHelper 
from ...models.db_engine.session import SessionManager
from ...models.genesis.utils import get_by_id_or_first_genesis_db_id

from ...datatables import DataTablesExt

logger = get_logger(app)
sm = SessionManager(app=app)

class DataTablesBlockHelper(DataTablesExt):
    pass

@app.route("/genesis/database/<int:id>/block_adv/<int:block_id>")
def block_adv(id, block_id):
    show_raw_data = bool(request.args.get("show_raw_data", False))
    model = BlockHelper 
    block = BlockChain.query.with_session(sm.get(id)).get(block_id)
    has_prev = block.has_prev(db_id=id)
    if has_prev:
        prev_block_id = block.prev(db_id=id).id
    else:
        prev_block_id = 0
    has_next = block.has_next(db_id=id)
    if has_next:
        next_block_id = block.next(db_id=id).id
    else:
        next_block_id = 0
    column_names = ['Title', 'Value']
    #id = db.Column(db.Integer, primary_key=True)
    #db_id = db.Column(db.Integer)
    #block_id = db.Column(db.Integer)
    #time = db.Column(db.Integer)
    #type = db.Column(db.Integer)
    #key_id = db.Column(db.String)
    #hash = db.Column(db.String)
    #contract_name = db.Column(db.String)
    #params = db.Column(db.String)
    bt_column_names = ['Time', 'Type', 'Key ID', 'Hash', 'Contract Name', 'Parameters']
    t_column_names = ['Time', 'Sender Key ID', 'Ecosystem ID',
                    'Hash', 'Type', 'Error']
    valid_db_id = get_by_id_or_first_genesis_db_id(id)
    return render_template('genesis/block_adv.html',
                            project=app.config.get('PRODUCT_BRAND_NAME') + ' Block Explorer',
                            db_id=id,
                            block_id=block_id,
                            block=block,
                            has_prev=has_prev,
                            has_next=has_next,
                            prev_block_id=prev_block_id,
                            next_block_id=next_block_id,
                            show_raw_data=show_raw_data,
                            column_names=column_names,
                            columns_num=len(column_names),
                            valid_db_id=valid_db_id,
                            hash_col_ind=3,
                            bt_column_names=bt_column_names,
                            bt_columns_num=len(bt_column_names),
                            t_column_names=t_column_names,
                            t_columns_num=len(t_column_names))

