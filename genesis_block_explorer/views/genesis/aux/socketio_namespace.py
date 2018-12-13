from threading import Lock
from flask import session, request
from flask_socketio import Namespace, emit, join_room, leave_room, \
    close_room, rooms, disconnect

class AuxNamespace(Namespace):
    def on_my_event(self, message):
        emit('my_response',
             {'data': message['data']})

    def on_my_broadcast_event(self, message):
        emit('my_response',
             {'data': message['data']}, broadcast=True)

    def on_disconnect_request(self):
        emit('my_response',
             {'data': 'Disconnected!'})
        disconnect()

    def on_my_ping(self):
        emit('my_pong')

    def on_connect(self):
        emit('my_response', {'data': 'Connected', 'count': 0})

    def on_disconnect(self):
        print('Client disconnected', request.sid)
