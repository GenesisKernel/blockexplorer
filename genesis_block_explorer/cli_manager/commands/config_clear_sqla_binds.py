""" The config-clear-sqla-bind command. """

from .base import Base, config_editor

class ConfigClearSqlaBinds(Base):
    """ Clear SQLAlchemy bind name/value in config """

    def run(self):
        config = config_editor.ConfigEditor(self.config_path)
        config.parse()
        config.parsed.clear_sqla_binds()
        config.parsed_to_content()
        config.save()
