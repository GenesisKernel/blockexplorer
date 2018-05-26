#! /usr/bin/env python

from genesis_block_explorer.app import create_app
app = create_app()
app.app_context().push()
app.run(host='127.0.0.1', debug = False)
