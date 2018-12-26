
import os
basedir = os.path.abspath(os.path.dirname(__file__))
PRODUCT_BRAND_NAME = 'Genesis'
PRODUCT_NAME = ('%s %s' % (PRODUCT_BRAND_NAME, 'Block Explorer'))
CSRF_ENABLED = True
SECRET_KEY = 'TWBt-1Cuz-GPtN-3vm2'
TIME_FORMAT = '%a, %d %b %Y %H:%M:%S'
CELERY_BROKER_URL = 'redis://localhost:16379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:16379/0'
REDIS_URL = 'redis://localhost:16379/0'
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
SQLALCHEMY_BINDS = {
    'db_engine': 'sqlite:///:memory:',
    'genesis_helpers': 'sqlite:///:memory:',
    'genesis1': 'postgresql://postgres:genesis@localhost:15432/genesis1',
    'genesis2': 'postgresql://postgres:genesis@localhost:15432/genesis2',
    'genesis3': 'postgresql://postgres:genesis@localhost:15432/genesis3',
    'genesis_blex_1': 'postgresql://postgres:genesis@localhost:15432/genesis_blex_1',
    'genesis_blex_2': 'postgresql://postgres:genesis@localhost:15432/genesis_blex_2',
    'genesis_blex_3': 'postgresql://postgres:genesis@localhost:15432/genesis_blex_3',
    'test_aux_genesis1': 'postgresql://postgres:genesis@localhost:15432/genesis_blex_1',
    'test_aux_genesis2': 'postgresql://postgres:genesis@localhost:15432/genesis_blex_2',
    'test_aux_genesis3': 'postgresql://postgres:genesis@localhost:15432/genesis_blex_3',
}
ENABLE_DATABASE_EXPLORER = True
ENABLE_DATABASE_SELECTOR = False
DB_ENGINE_DISCOVERY_MAP = {
    'genesis1': {
        'backend_version': '20180512',
    },
    'genesis2': {
        'backend_version': '20180512',
    },
    'genesis3': {
        'backend_version': '20180512',
    },
}
AUX_HELPERS_BIND_NAME = 'aux_genesis_helpers'
AUX_DB_ENGINE_DISCOVERY_MAP = {
    'genesis_blex_1': {
        'backend_version': '20180512',
    },
    'genesis_blex_2': {
        'backend_version': '20180512',
    },
    'genesis_blex_3': {
        'backend_version': '20180512',
    },
    'test_aux_genesis1': {
        'backend_version': '20180512',
    },
    'test_aux_genesis2': {
        'backend_version': '20180512',
    },
    'test_aux_genesis3': {
        'backend_version': '20180512',
    },
}
SOCKETIO_HOST = '127.0.0.1'
SOCKETIO_PORT = 8080
FETCH_NUM_OF_BLOCKS = 50
BACKEND_API_URLS = {
    1: 'http://localhost:17301/api/v2',
    2: 'http://localhost:17302/api/v2',
    3: 'http://localhost:17303/api/v2',
}
BACKEND_VERSION_FEATURES_MAP = {
    '20180830': {
        'github-branch': 'master',
        'github-commmit': ' e5ddc76',
        'url': 'https://github.com/GenesisKernel/go-genesis/pull/513',
        'features': ['blocks_tx_info_api_endpoint', 'system_parameters_at_ecosystem', 'image_id_instead_of_avatar', 'member_info_at_members', 'keys_tables_delete_to_blocked'],
    },
    '20180512': {
        'github-branch': 'develop',
        'github-commmit': '4b69b8e',
        'url': 'https://github.com/GenesisKernel/go-genesis/pull/290',
        'features': ['system_parameters_at_ecosystem', 'image_id_instead_of_avatar', 'member_info_at_members'],
    },
}
DISKCACHE_PATH = '/tmp/genesis_block_explorer_diskcache'
DISKCACHE_DBEX_DATABASE_TIMEOUT = 10000
POSTS_PER_PAGE = 3
MAX_SEARCH_RESULTS = 50
