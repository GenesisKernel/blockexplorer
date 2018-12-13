""" The config-clear-db-engines command. """

from .base import Base, config_editor

class ConfigClearDbEngines(Base):
    """ Clear DB Engine/Params in config """

    def run(self):
        config = config_editor.ConfigEditor(self.config_path)
        config.parse()
        config.parsed.clear_db_engines()
        config.parsed_to_content()
        config.save()
