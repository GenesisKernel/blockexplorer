""" The add-be-url command. """

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

class AddBeUrl(Base):
    """ Add Backend API URL to config """

    def run(self):
        config_path = get_config_path(self.options.get("--config-path"))
        config = config_editor.ConfigEditor(config_path)
        name = self.options.get("--name") 
        value = self.options.get("--value")
        if name and value:
            config.parse()
            config.parsed.add_be_url(name, value)
            config.parsed_to_content()
            config.save()
