import os

from setuptools import setup, find_packages

__VERSION__ = '0.1.0'

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
    'psycopg2',
    'inflect',
    'dictalchemy',
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
)
