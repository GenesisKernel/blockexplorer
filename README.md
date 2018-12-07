Genesis Block Explorer
======================

## Status
Under heavy development

## How to run

### webserver

gunicorn -b 127.0.0.1:8000 --worker-class eventlet -w 1 genesis_block_explorer.socketio:app

### worker

celery -A genesis_block_explorer.celery.tasks worker

### beat

celery -A genesis_block_explorer.celery.tasks beat
