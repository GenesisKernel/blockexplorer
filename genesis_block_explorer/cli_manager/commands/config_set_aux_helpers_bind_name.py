""" The config-set-socketio-host command. """

from .base import Base, config_editor

class ConfigSetAuxHelpersBindName(Base):
    """ Set Aux Helpers Bind Name to config """

    def run(self):
        config = config_editor.ConfigEditor(self.config_path)
        value = self.options.get("<value>")
        config.parse()
        config.parsed.set_aux_helpers_bind_name(value)
        config.parsed_to_content()
        config.save()
