""" The config-clear-aux-db-engines command. """

from .base import Base, config_editor

class ConfigClearAuxDbEngines(Base):
    """ Clear Aux DB Engine/Params in config """

    def run(self):
        config = config_editor.ConfigEditor(self.config_path)
        config.parse()
        config.parsed.clear_aux_db_engines()
        config.parsed_to_content()
        config.save()
