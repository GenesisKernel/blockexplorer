""" The config-add-sqla-bind command. """

from .base import Base, config_editor

class ConfigAddSqlaBind(Base):
    """ Add SQLAlchemy bind name/value pair to config """

    def run(self):
        config = config_editor.ConfigEditor(self.config_path)
        name = self.options.get("--name") 
        value = self.options.get("--value")
        if name and value:
            config.parse()
            config.parsed.add_sqla_bind(name, value)
            config.parsed_to_content()
            config.save()
