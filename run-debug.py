#! /usr/bin/env python

from genesis_block_explorer.socketio import socketio, app

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', debug=True)
    #app.run(host='0.0.0.0', debug = True)
