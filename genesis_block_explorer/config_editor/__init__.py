import ast
import astunparse
import autopep8

from ..utils import to_bool

class Config:
    def load(self):
        self.config_file = open(self.config_path, 'rb')
        self.content = self.config_file.read()
        self.config_file.close()

    def save(self, save_config_path=None):
        if not save_config_path:
            if self.save_to_same_file:
                save_config_path = self.config_path
            else:
                save_config_path = self.config_path + '.updated'
        save_config_file = open(save_config_path, 'wb')
        if self.use_autopep8:
            self.content = autopep8.fix_code(self.content,
                                             self.autopep8_options).encode()
        save_config_file.write(self.content)
        save_config_file.close()

    def __init__(self, config_path, **kwargs):
        self.config_path = config_path
        self.use_autopep8 = kwargs.get('use_autopep8', True)
        self.autopep8_options = kwargs.get('autopep8_options',
                                           {'aggressive': 1})
        self.save_to_same_file = kwargs.get('save_to_same_file', True)
        self.load()

class ConfigParsed:
    def __init__(self, source):
        self.parsed = ast.parse(source)

    def find_enable_database_explorer(self):
        return [x for x in ast.walk(self.parsed) if isinstance(x, ast.Assign) and x.targets and x.targets[0].id == 'ENABLE_DATABASE_EXPLORER']

    def find_enable_database_selector(self):
        return [x for x in ast.walk(self.parsed) if isinstance(x, ast.Assign) and x.targets and x.targets[0].id == 'ENABLE_DATABASE_SELECTOR']

    def find_redis_url(self):
        return [x for x in ast.walk(self.parsed) if isinstance(x, ast.Assign) and x.targets and x.targets[0].id == 'REDIS_URL']

    def find_celery_broker_url(self):
        return [x for x in ast.walk(self.parsed) if isinstance(x, ast.Assign) and x.targets and x.targets[0].id == 'CELERY_BROKER_URL']

    def find_celery_result_backend(self):
        return [x for x in ast.walk(self.parsed) if isinstance(x, ast.Assign) and x.targets and x.targets[0].id == 'CELERY_RESULT_BACKEND']

    def find_socketio_host(self):
        return [x for x in ast.walk(self.parsed) if isinstance(x, ast.Assign) and x.targets and x.targets[0].id == 'SOCKETIO_HOST']

    def find_socketio_port(self):
        return [x for x in ast.walk(self.parsed) if isinstance(x, ast.Assign) and x.targets and x.targets[0].id == 'SOCKETIO_PORT']

    def find_aux_helpers_bind_name(self):
        return [x for x in ast.walk(self.parsed) if isinstance(x, ast.Assign) and x.targets and x.targets[0].id == 'AUX_HELPERS_BIND_NAME']

    def find_backend_api_urls(self):
        return [x for x in ast.walk(self.parsed) if isinstance(x, ast.Assign) and x.targets and x.targets[0].id == 'BACKEND_API_URLS']

    def find_db_engine_discovery_map(self):
        return [x for x in ast.walk(self.parsed) if isinstance(x, ast.Assign) and x.targets and x.targets[0].id == 'DB_ENGINE_DISCOVERY_MAP']

    def find_aux_db_engine_discovery_map(self):
        return [x for x in ast.walk(self.parsed) if isinstance(x, ast.Assign) and x.targets and x.targets[0].id == 'AUX_DB_ENGINE_DISCOVERY_MAP']

    def find_sqla_binds(self):
        return [x for x in ast.walk(self.parsed) if isinstance(x, ast.Assign) and x.targets and x.targets[0].id == 'SQLALCHEMY_BINDS']

    def set_enable_database_explorer(self, value):
        for ede in self.find_enable_database_explorer(): 
            ede.value = ast.NameConstant(to_bool(value))

    def set_enable_database_selector(self, value):
        for eds in self.find_enable_database_selector(): 
            eds.value = ast.NameConstant(to_bool(value))

    def set_redis_url(self, value):
        for redis_url in self.find_redis_url(): 
            redis_url.value = ast.Str(s=value)

    def set_celery_broker_url(self, value):
        for cbu in self.find_celery_broker_url(): 
            cbu.value = ast.Str(s=value)

    def set_celery_result_backend(self, value):
        for crb in self.find_celery_result_backend(): 
            crb.value = ast.Str(s=value)

    def set_socketio_host(self, value):
        for socketio_host in self.find_socketio_host(): 
            socketio_host.value = ast.Str(s=value)

    def set_socketio_port(self, value):
        for socketio_port in self.find_socketio_port(): 
            socketio_port.value = ast.Num(n=int(value))

    def set_aux_helpers_bind_name(self, value):
        for aux_helpers_bind_name in self.find_aux_helpers_bind_name(): 
            aux_helpers_bind_name.value = ast.Str(s=value)

    def add_sqla_bind(self, name, value):
        for sqla_bind in self.find_sqla_binds():
            sqla_bind.value.keys.append(ast.Str(s=name))
            sqla_bind.value.values.append(ast.Str(s=value))

    def clear_sqla_binds(self):
        for sqla_bind in self.find_sqla_binds():
            sqla_bind.value.keys.clear()
            sqla_bind.value.values.clear()

    def add_backend_api_url(self, name, value):
        for bau in self.find_backend_api_urls():
            bau.value.keys.append(ast.Num(n=int(name)))
            bau.value.values.append(ast.Str(s=value))

    def clear_backend_api_urls(self):
        for bau in self.find_backend_api_urls():
            bau.value.keys.clear()
            bau.value.values.clear()

    def add_db_engine(self, bind_name, backend_version):
        for dbe in self.find_db_engine_discovery_map():
            dict_keys = [ast.Str(s='backend_version')]
            dict_values = [ast.Str(s=backend_version)]
            _dict = ast.Dict(keys=dict_keys, values=dict_values)
            dbe.value.keys.append(ast.Str(s=bind_name))
            dbe.value.values.append(_dict)

    def clear_db_engines(self):
        for dbe in self.find_db_engine_discovery_map():
            dbe.value.keys.clear()
            dbe.value.values.clear()

    def add_aux_db_engine(self, bind_name, backend_version):
        for dbe in self.find_aux_db_engine_discovery_map():
            dict_keys = [ast.Str(s='backend_version')]
            dict_values = [ast.Str(s=backend_version)]
            _dict = ast.Dict(keys=dict_keys, values=dict_values)
            dbe.value.keys.append(ast.Str(s=bind_name))
            dbe.value.values.append(_dict)

    def clear_aux_db_engines(self):
        for dbe in self.find_aux_db_engine_discovery_map():
            dbe.value.keys.clear()
            dbe.value.values.clear()

    def to_source(self):
        return astunparse.unparse(self.parsed)

class ConfigEditor(Config):
    def parse(self):
        self.parsed = ConfigParsed(self.content)

    def parsed_to_content(self):
        self.content = self.parsed.to_source()

