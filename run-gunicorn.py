#! /usr/bin/env python

from genesis_block_explorer.app import create_app
app = create_app(debug=True)
#app.app_context().push()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug = True)
