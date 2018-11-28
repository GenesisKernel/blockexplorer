""" The config-clear-backend-api-urls command. """

from .base import Base, config_editor

class ConfigClearBackendApiUrls(Base):
    """ Clear Backend API URLs in config """

    def run(self):
        config = config_editor.ConfigEditor(self.config_path)
        config.parse()
        config.parsed.clear_backend_api_urls()
        config.parsed_to_content()
        config.save()
