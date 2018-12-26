""" The config-set-socketio-host command. """

from .base import Base, config_editor

class ConfigSetSocketioPort(Base):
    """ Set Socketio Port to config """

    def run(self):
        config = config_editor.ConfigEditor(self.config_path)
        value = self.options.get("<value>")
        config.parse()
        config.parsed.set_socketio_port(value)
        config.parsed_to_content()
        config.save()
