import ast
import astunparse
import autopep8
import distutils

def to_bool(value):
    if str(value).lower() in ("yes", "y", "true",  "t", "1", "enable", "allow", "permit"):
        return True
    elif str(value).lower() in ("no",  "n", "false", "f", "0", "0.0", "", "none", "[]", "{}", "disable", "deny", "reject"):
        return False
    else:
        return False

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

    def set_enable_database_explorer(self, value):
        _value = ast.NameConstant(to_bool(value))
        for ede in self.find_enable_database_explorer(): 
            ede.value = _value

    def set_enable_database_selector(self, value):
        _value = ast.NameConstant(to_bool(value))
        for eds in self.find_enable_database_selector(): 
            eds.value = _value

    def set_redis_url(self, value):
        _value = ast.Str(s=value)
        for redis_url in self.find_redis_url(): 
            redis_url.value = _value

    def set_celery_broker_url(self, value):
        _value = ast.Str(s=value)
        for cbu in self.find_celery_broker_url(): 
            cbu.value = _value

    def set_celery_result_backend(self, value):
        _value = ast.Str(s=value)
        for crb in self.find_celery_result_backend(): 
            crb.value = _value

    def set_socketio_host(self, value):
        _value = ast.Str(s=value)
        for socketio_host in self.find_socketio_host(): 
            socketio_host.value = _value

    def set_socketio_port(self, value):
        _value = ast.Num(n=int(value))
        for socketio_port in self.find_socketio_port(): 
            socketio_port.value = _value

    def set_aux_helpers_bind_name(self, value):
        _value = ast.Str(s=value)
        for aux_helpers_bind_name in self.find_aux_helpers_bind_name(): 
            aux_helpers_bind_name.value = _value

    def add_bind(self, name, value):
        for sqla_bind in self.find_sqla_binds():
            _name = ast.Str(s=name)
            _value = ast.Str(s=value)
            sqla_bind.value.keys.append(_name)
            sqla_bind.value.values.append(_value)

    def add_be_url(self, name, value):
        for be_api_url in self.find_backend_api_urls():
            _name = ast.Num(n=int(name))
            _value = ast.Str(s=value)
            be_api_url.value.keys.append(_name)
            be_api_url.value.values.append(_value)

    def add_db_engine(self, bind_name, backend_version):
        for db_engine in self.find_db_engine_discovery_map():
            _bind_name = ast.Str(s=bind_name)
            dict_keys = [ast.Str(s='backend_version')]
            dict_values = [ast.Str(s=backend_version)]
            _dict = ast.Dict(keys=dict_keys, values=dict_values)
            db_engine.value.keys.append(_bind_name)
            db_engine.value.values.append(_dict)

    def add_aux_db_engine(self, bind_name, backend_version):
        for db_engine in self.find_aux_db_engine_discovery_map():
            _bind_name = ast.Str(s=bind_name)
            dict_keys = [ast.Str(s='backend_version')]
            dict_values = [ast.Str(s=backend_version)]
            _dict = ast.Dict(keys=dict_keys, values=dict_values)
            db_engine.value.keys.append(_bind_name)
            db_engine.value.values.append(_dict)

    def to_source(self):
        return astunparse.unparse(self.parsed)

class ConfigEditor(Config):
    def parse(self):
        self.parsed = ConfigParsed(self.content)

    def parsed_to_content(self):
        self.content = self.parsed.to_source()

