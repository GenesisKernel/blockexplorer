from flask import render_template, current_app as app

from ..models.genesis.utils import get_by_id_or_first_genesis_db_id

def get_async_mode():
    return "dummy"

@app.route("/")
def home():
    valid_db_id = get_by_id_or_first_genesis_db_id()
    return render_template('home.html',
                           project=app.config.get('PRODUCT_BRAND_NAME') + ' Block Explorer',
                           valid_db_id=valid_db_id,
                           seq_num=valid_db_id,
                           async_mode=get_async_mode(),
                           socketio_namespace='/backend%d' % valid_db_id)

