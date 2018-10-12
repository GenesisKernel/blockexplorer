from threading import Lock
from flask import request
from flask_socketio import SocketIO

from .app import create_app, create_lean_app
from .views.genesis.aux.socketio_namespace import AuxNamespace
#from .views.genesis.aux.socketio import AuxNamespace
from .models.genesis.aux.config import get_num_of_backends

app = create_app(debug=True)
app.app_context().push()

thread = None
thread_lock = Lock()

async_mode = None
socketio = SocketIO(app, async_mode=async_mode)

for i in range(1, get_num_of_backends(app) + 1):
    socketio.on_namespace(AuxNamespace('/backend%d' % i))

#socketio.on_namespace(AuxNamespace('/backend%d' % 1))
#socketio.on_namespace(AuxNamespace('/backend1'))
#socketio.on_namespace(AuxNamespace('/test'))
#if __name__ == '__main__':
#    socketio.run(app, debug=True)
