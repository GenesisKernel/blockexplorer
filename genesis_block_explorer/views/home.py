from flask import render_template, current_app as app

from ..models.genesis.utils import get_by_id_or_first_genesis_db_id

@app.route("/")
def home():
    valid_db_id = get_by_id_or_first_genesis_db_id()
    return render_template('home.html', project='genesis block explorer',
                           valid_db_id=valid_db_id)
