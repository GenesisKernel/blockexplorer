import os

from setuptools import setup, find_packages

__VERSION__ = '0.3.1'

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.md')) as f:
    README = f.read()

requires = [
    'sqlalchemy-datatables',
    'Flask',
    'jinja2',
    'Flask-SQLAlchemy',
    'Flask-RESTful',
    'Flask-JWT',
    'psycopg2-binary',
    'inflect',
    'dictalchemy',
    'six',
    'pytz',
    'aniso8601',
    'jwt',
    'Flask-JsonTools',
    'msgpack',
    'attrdict',
    'gunicorn',
    'astunparse',
    'docopt',
    'autopep8',
    'genesis-blockchain-tools',
    'genesis-blockchain-api-client',
    'nose',
    'celery',
    'redis==4.5.3',
    'Flask-SocketIO',
    'eventlet',
    'socketIO-client',
    'diskcache',
    'tcpping',
]

dependency_links = [
    'git+https://github.com/blitzstern5/genesis-blockchain-api-client#egg=genesis-blockchain-api-client',
    'git+https://github.com/blitzstern5/genesis-blockchain-tools#egg=genesis-blockchain-tools',
]

setup(
    name='genesis_block_explorer',
    version=__VERSION__,
    description='Genesis Block Explorer',
    long_description=README,
    classifiers=[
        "Programming Language :: Python",
        "Framework :: Flask",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
    ],
    author='blitzstern5',
    author_email='blitzstern5@gmail.com',
    url='https://github.com/blitzstern5/genesis-block-explorer',
    keywords='web wsgi bfg flask',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    test_suite='genesis_block_explorer',
    install_requires=requires,
    dependency_links=dependency_links,
)
