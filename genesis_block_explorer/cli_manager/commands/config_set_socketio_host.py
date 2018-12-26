""" The config-set-socketio-host command. """

from .base import Base, config_editor

class ConfigSetSocketioHost(Base):
    """ Set Socketio Host to config """

    def run(self):
        config = config_editor.ConfigEditor(self.config_path)
        value = self.options.get("<value>")
        config.parse()
        config.parsed.set_socketio_host(value)
        config.parsed_to_content()
        config.save()
