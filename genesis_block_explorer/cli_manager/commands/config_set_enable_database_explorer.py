""" The config-set-enable-database-explorer command. """

from .base import Base, config_editor

class ConfigSetEnableDatabaseExplorer(Base):
    """ Set Enable Database Explorer to config """

    def run(self):
        config = config_editor.ConfigEditor(self.config_path)
        value = self.options.get("<value>")
        config.parse()
        config.parsed.set_enable_database_explorer(value)
        config.parsed_to_content()
        config.save()
