Genesis Block Explorer
======================

## Status
Under heavy development

## How to run

### Gunicorn

#### eventlet

gunicorn -b 127.0.0.1:8000 --worker-class eventlet -w 1 genesis_block_explorer.socketio:app

#### celery worker

celery -A genesis_block_explorer.celery.tasks worker

#### celery beat

celery -A genesis_block_explorer.celery.tasks beat
