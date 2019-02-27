# Genesis Block Explorer

## How to run

### Requirements

Install redis server and python packages from requirements.txt

### Config

Create config.py and choose appropriate options

### Run Web Server

```
gunicorn -b 127.0.0.1:8000 --worker-class eventlet -w 1 genesis_block_explorer.socketio:app
```

### Run Worker/Beat Services

```
celery -B -A genesis_block_explorer.celery.tasks worker
```

