""" The config-set-redis-url command. """

from .base import Base, config_editor

class ConfigSetRedisUrl(Base):
    """ Set Redis URL to config """

    def run(self):
        config = config_editor.ConfigEditor(self.config_path)
        value = self.options.get("<value>")
        config.parse()
        config.parsed.set_redis_url(value)
        config.parsed_to_content()
        config.save()
