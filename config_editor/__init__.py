import ast
import astunparse
import autopep8

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
        self.save_to_same_file = kwargs.get('save_to_same_file', False)
        self.load()

class ConfigParsed:
    def __init__(self, source):
        self.parsed = ast.parse(source)

    def find_sqla_binds(self):
        return [x for x in ast.walk(self.parsed) if isinstance(x, ast.Assign) and x.targets and x.targets[0].id == 'SQLALCHEMY_BINDS']

    def add_bind(self, name, value):
        for sqla_bind in self.find_sqla_binds():
            print("FOUND sqla_bind, adding %s: %s" % (name, value))
            _name = ast.Str(s=name)
            _value = ast.Str(s=value)
            sqla_bind.value.keys.append(_name)
            sqla_bind.value.values.append(_value)

    def to_source(self):
        return astunparse.unparse(self.parsed)

class ConfigEditor(Config):
    def parse(self):
        self.parsed = ConfigParsed(self.content)

    def parsed_to_content(self):
        self.content = self.parsed.to_source()

