import os
from flask import Flask, g

def start_db_for_app(app):
    if 'start_db_for_app_counter' not in g:
        g.start_db_for_app_counter = 0
    g.start_db_for_app_counter += 1
    app.logger.debug("started g.start_db_for_app_counter: %d" % g.start_db_for_app_counter)
    from .models.db_engine.database import (
        Database, Table, db,
        init_db as init_db_engine_db, 
        import_data as import_db_engine_data
    )
    from .models.db_engine.automap import (
        import_automapped_data, automapped_classes
    )
    from .models.genesis.helpers import (
        FullNode, init_db as init_genesis_helpers_db
    )
    with app.app_context():
        init_db_engine_db()
        init_genesis_helpers_db()
        import_db_engine_data(app)
        mcn = import_automapped_data(app, use_automapped_classes=True,
                                          use_no_pk_tables=True)
    app.logger.debug("Database.query.all(): %s" % str(Database.query.all()))
    app.logger.debug("Table.query.all(): %s" % str(Table.query.all()))
    return app

def start_db_for_app_once(app):
    if 'start_db_for_app_counter' not in g:
        g.start_db_for_app_counter = 0
    if g.start_db_for_app_counter > 0:
        return app
    return start_db_for_app(app)

def create_lean_app(**kwargs):
    app = Flask(__name__)

    app.config.from_pyfile('../config.py')
    if kwargs.get('debug', False):
        app.config['DEBUG'] = True

def create_app(**kwargs):
    app = Flask(__name__)

    app.config.from_pyfile('../config.py')
    if kwargs.get('debug', False):
        app.config['DEBUG'] = True

    from .json import CustomJSONEncoder
    app.json_encoder = CustomJSONEncoder

    from .logging import handler as logging_handler, level as logging_level
    app.logger.addHandler(logging_handler)
    app.logger.debug("kwargs: %s" % kwargs)

    with app.app_context():
        from .db import db
        db.init_app(app)
        if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
            start_db_for_app_once(app)

        from .views import home
        from .views.db_engine import databases, tables, columns, values
        from .views.genesis import (
            blocks, blocks_adv, block, block_adv, block_new,
            ecosystems, ecosystem_members, ecosystem_params, ecosystem_adv,
            sys_params, sys_params_adv, full_nodes,
            transactions, transactions_by_block, transaction
        )

    return app

