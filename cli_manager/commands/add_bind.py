""" The add-bind command. """

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

class AddBind(Base):
    """ Add SQLAlchemy bind name/value pair to config """

    def run(self):
        #print('Adding bind!')
        print('You supplied the following options:', dumps(self.options, indent=2, sort_keys=True))
        #print("script path: %s" % get_script_path())
        config_path = get_config_path(self.options.get("--config-path"))

        print("config path: %s" % config_path)
        config = config_editor.ConfigEditor(config_path)
        name = self.options.get("--name") 
        value = self.options.get("--value")
        if name and value:
            config.parse()
            config.parsed.add_bind(name, value)
            config.parsed_to_content()
            config.save()
        print("config: %s" % config.content)
