""" The add-aux-db-engine command. """

from json import dumps

from .base import Base

import os
import sys

import config_editor

def get_script_path():
    return os.path.dirname(os.path.realpath(sys.argv[0]))

def get_config_path(config_path=None):
    if config_path:
        return os.path.abspath(config_path)
    else:
        return os.path.join(os.path.dirname(get_script_path()), 'config.py')

class AddAuxDbEngine(Base):
    """ Add Aux DB Engine/Params to config """

    def run(self):
        config_path = get_config_path(self.options.get("--config-path"))

        config = config_editor.ConfigEditor(config_path)
        bind_name = self.options.get("--bind-name") 
        backend_version = self.options.get("--backend-version")
        if bind_name and backend_version:
            config.parse()
            config.parsed.add_aux_db_engine(bind_name, backend_version)
            config.parsed_to_content()
            config.save()
