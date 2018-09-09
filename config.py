import os
basedir = os.path.abspath(os.path.dirname(__file__))

PRODUCT_BRAND_NAME = "Apla"

CSRF_ENABLED = True
SECRET_KEY = 'TWBt-1Cuz-GPtN-3vm2'

SQLALCHEMY_TRACK_MODIFICATIONS = False

SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
SQLALCHEMY_BINDS = {
    'db_engine': 'sqlite:///:memory:',
    'genesis_helpers'  : 'sqlite:///:memory:',
    #'genesis_aux': 'sqlite:///' + os.path.join(basedir, 'genesis_aux.sqlite'),
    'genesis_aux_test': 'sqlite:///' + os.path.join(basedir, 'genesis_aux_test.sqlite'),
    'genesis1': 'postgresql://postgres:genesis@localhost:15432/genesis1',
}

DB_ENGINE_DISCOVERY_MAP = {
    'genesis1': { 'backend_version': 20180830 },
}

AUX_DB_ENGINE_DISCOVERY_MAP = {
    'genesis_aux_test': { 'backend_version': 20180830 },
    #'genesis_aux_test_1': { 'backend_version': 20180830 },
}

BACKEND_API_URLS = {
    1: 'http://localhost:17301/api/v2',
    2: 'http://localhost:17302/api/v2',
    3: 'http://localhost:17303/api/v2',
    4: 'http://localhost:17304/api/v2',
    5: 'http://localhost:17305/api/v2',
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

POSTS_PER_PAGE = 3
MAX_SEARCH_RESULTS = 50
