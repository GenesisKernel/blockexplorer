class AppConfig:
    def __init__(self, app, **kwargs):
        self.app = app 

    def add_prefix_to_param_str_value(self, name, prefix):
        assert name in self.app.config
        self.app.config[name] = prefix + self.app.config[name]

    def add_prefix_to_param_dict_keys(self, name, prefix):
        assert name in self.app.config
        new_d = {prefix + k: v for k, v in self.app.config.get(name).items()}
        self.app.config[name] = new_d
