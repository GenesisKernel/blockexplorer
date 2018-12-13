""" The config-set-celery-result-backend command. """

from .base import Base, config_editor

class ConfigSetCeleryResultBackend(Base):
    """ Set Celery Result Backend to config """

    def run(self):
        config = config_editor.ConfigEditor(self.config_path)
        value = self.options.get("<value>")
        config.parse()
        config.parsed.set_celery_result_backend(value)
        config.parsed_to_content()
        config.save()
