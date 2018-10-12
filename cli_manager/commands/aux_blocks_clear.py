""" Clear blocks @ auxliliary DB """

import os
import sys

from genesis_block_explorer.app import create_lean_app as create_app
from genesis_block_explorer.models.genesis.aux.block.filler import BlockFiller
from genesis_block_explorer.models.genesis.aux.session import (
    AuxSessionManager as SessionManager, 
)

from .base import Base

class AuxBlocksClear(Base):
    def run(self):
        seq_num = self.options.get("<seq-num>")
        app = create_app()
        app.app_context().push()
        sm = SessionManager(app=app)
        session = sm.get_session(seq_num)
        bf = BlockFiller(app=app, seq_num=seq_num)
        bf.clear()
