""" The config-add-backend-api-url command. """

from .base import Base, config_editor

class ConfigAddBackendApiUrl(Base):
    """ Add Backend API URL to config """

    def run(self):
        config = config_editor.ConfigEditor(self.config_path)
        name = self.options.get("--name") 
        value = self.options.get("--value")
        if name and value:
            config.parse()
            config.parsed.add_backend_api_url(name, value)
            config.parsed_to_content()
            config.save()
