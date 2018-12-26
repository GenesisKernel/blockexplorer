import os
import argparse

from flask import Flask, g

from .utils import to_bool

def get_default_config_path():
    return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config.py')

def get_args(**kwargs):
    parser = argparse.ArgumentParser()
    parser.add_argument('--config',
                        default=get_default_config_path(),
                        help='Path to configuration file')
    parser.add_argument('--debug', dest='debug', action='store_true',
                        help='Run in debug mode')
    parser.add_argument('--no-debug', dest='debug', action='store_false',
                        help='Run in non-debug mode')
    parser.set_defaults(debug=False)
    if kwargs.get('allow_unknown_args', True):
        args, unknown = parser.parse_known_args()
        return args
    else:
        return parser.parse_args()

def get_config_path(*args, **kwargs):
    if len(args) > 0 and args[0]:
        return args[0]
    else:
        return os.path.abspath(get_args(**kwargs).config)

def get_debug_mode():
    return to_bool(os.environ.get('DEBUG') or get_args().debug)

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

    config_path = kwargs.get('config_path',
                             os.environ.get('CONFIG', get_config_path()))
    if config_path:
        app.config.from_pyfile(config_path)
    if kwargs.get('debug', False):
        app.config['DEBUG'] = True
    with app.app_context():
        from .db import db
        db.init_app(app)
    return app

def create_app(**kwargs):
    app = Flask(__name__)

    config_path = kwargs.get('config_path',
                             os.environ.get('CONFIG', get_config_path()))
    if config_path:
        app.config.from_pyfile(config_path)
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
        #if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        #    start_db_for_app_once(app)
        start_db_for_app_once(app)

        from .models.genesis.aux.table import TableManager
        TableManager(app=app).create_tables()

        from .views import home

        if app.config.get('ENABLE_DATABASE_EXPLORER') \
        or app.config.get('ENABLE_DATABASE_SELECTOR'):
            from .views.db_engine import databases

        if app.config.get('ENABLE_DATABASE_EXPLORER'):
            from .views.db_engine import tables, columns, values

        from .views.genesis import (
            blocks, blocks_adv, block, block_adv, block_transactions,
            ecosystems, ecosystem_members, ecosystem_params, ecosystem_adv,
            sys_params, sys_params_adv, full_nodes,
            transactions, transactions_by_block, transaction
        )
        #from .views.genesis.aux.filler import (
        #    filler_test_add, filler_test_add_result,
        #    filler_update, filler_update_result,
        #)
        from .views.genesis.aux.blocks import (
            aux_blocks, dt_aux_blocks,
        )
        from .views.genesis.aux.block import (
            aux_block, dt_aux_block_helper,
        )
        from .views.genesis.aux.transactions import (
            aux_transactions, dt_aux_transactions,
        )
        from .views.genesis.aux.transaction import (
            aux_transaction, dt_aux_transaction_helper,
        )

    return app

#if __name__ == '__main__':
#    print("args: %s" % get_args)
