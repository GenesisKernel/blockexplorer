import os
basedir = os.path.abspath(os.path.dirname(__file__))

PRODUCT_BRAND_NAME = "Unknown"
PRODUCT_NAME = "%s %s" % (PRODUCT_BRAND_NAME, "Block Explorer")

CSRF_ENABLED = True
SECRET_KEY = 'no-secret-key'

TIME_FORMAT = '%a, %d %b %Y %H:%M:%S'
CELERY_BROKER_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'

REDIS_HOST = os.environ.get('REDIS_HOST') or 'localhost'
REDIS_PORT = os.environ.get('REDIS_PORT') or 6379
REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD') or ''
REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'

SQLALCHEMY_TRACK_MODIFICATIONS = False

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'default.sqlite')
SQLALCHEMY_BINDS = {
    'db_engine': 'sqlite:///' + os.path.join(basedir, 'db_engine.sqlite'),
    'genesis_helpers': 'sqlite:///' + os.path.join(basedir, 'helpers.sqlite'),
    'aux_genesis_helpers': 'sqlite:///' + os.path.join(basedir, 'aux_helpers.sqlite'),

    #'aux_genesis1': 'sqlite:///' + os.path.join(basedir, 'aux_genesis1.sqlite'),
    #'aux_genesis2': 'sqlite:///' + os.path.join(basedir, 'aux_genesis2.sqlite'),
    #'aux_genesis3': 'sqlite:///' + os.path.join(basedir, 'aux_genesis3.sqlite'),
}

ENABLE_DATABASE_EXPLORER = False
ENABLE_DATABASE_SELECTOR = True

DB_ENGINE_DISCOVERY_MAP = {
    #'genesis1': { 'backend_version': '20180830' },
    #'genesis2': { 'backend_version': '20180830' },
    #'genesis3': { 'backend_version': '20180830' },
}

AUX_HELPERS_BIND_NAME = 'aux_genesis_helpers'

AUX_DB_ENGINE_DISCOVERY_MAP = {
    #'aux_genesis1': { 'backend_version': '20180830' },
    #'aux_genesis2': { 'backend_version': '20180830' },
    #'aux_genesis3': { 'backend_version': '20180830' },
}

FETCH_NUM_OF_BLOCKS = 50

BACKEND_API_URLS = {
    #1: 'http://localhost:17301/api/v2',
    #2: 'http://localhost:17302/api/v2',
    #3: 'http://localhost:17303/api/v2',
}

BACKEND_VERSION_FEATURES_MAP = {
    '20180830': {
        'github-branch': 'master',
        'github-commmit': ' e5ddc76',
        'url': 'https://github.com/GenesisKernel/go-genesis/pull/513',
        'features': [
            'blocks_tx_info_api_endpoint',
            'system_parameters_at_ecosystem',
            'image_id_instead_of_avatar',
            'member_info_at_members',
            'keys_tables_delete_to_blocked',
        ]
    },
    '20180512': {
        'github-branch': 'develop',
        'github-commmit': '4b69b8e',
        'url': 'https://github.com/GenesisKernel/go-genesis/pull/290',
        'features': [
            'system_parameters_at_ecosystem',
            'image_id_instead_of_avatar',
            'member_info_at_members',
        ]
    }
}

DISKCACHE_PATH = '/tmp/genesis_block_explorer_diskcache'
DISKCACHE_DBEX_DATABASE_TIMEOUT = 10000

POSTS_PER_PAGE = 3
MAX_SEARCH_RESULTS = 50

