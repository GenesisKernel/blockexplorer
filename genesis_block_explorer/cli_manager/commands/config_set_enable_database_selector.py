""" The config-set-enable-database-selector command. """

from .base import Base, config_editor

class ConfigSetEnableDatabaseSelector(Base):
    """ Set Enable Database Selector to config """

    def run(self):
        config = config_editor.ConfigEditor(self.config_path)
        value = self.options.get("<value>")
        config.parse()
        config.parsed.set_enable_database_selector(value)
        config.parsed_to_content()
        config.save()
