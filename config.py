import os
basedir = os.path.abspath(os.path.dirname(__file__))

CSRF_ENABLED = True
SECRET_KEY = 'TWBt-1Cuz-GPtN-3vm2'

SQLALCHEMY_TRACK_MODIFICATIONS = False

SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
SQLALCHEMY_BINDS = {
    'db_engine': 'sqlite:///:memory:',
    'genesis_helpers'  : 'sqlite:///:memory:',
}

DB_ENGINE_DISCOVERY_MAP = {
}

BACKEND_VERSION_FEATURES_MAP = {
    20180512: {
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
