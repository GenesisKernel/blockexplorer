""" The config-add-aux-db-engine command. """

from .base import Base, config_editor

class ConfigAddAuxDbEngine(Base):
    """ Add Aux DB Engine/Params to config """

    def run(self):
        config = config_editor.ConfigEditor(self.config_path)
        bind_name = self.options.get("--bind-name") 
        backend_version = self.options.get("--backend-version")
        if bind_name and backend_version:
            config.parse()
            config.parsed.add_aux_db_engine(bind_name, backend_version)
            config.parsed_to_content()
            config.save()
