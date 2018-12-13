from nose import with_setup

import string
import random

from genesis_block_explorer.app import create_lean_app as create_app
from genesis_block_explorer.config_utils import AppConfig

def my_setup():
    pass

def my_teardown():
    pass

def mk_randword(length, up=False):
    if up:
        letters = string.ascii_uppercase
    else:
        letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

@with_setup(my_setup, my_teardown)
def test_add_prefix_to_param_str_value():
    app = create_app()
    param = mk_randword(8, up=True) + '_STR'
    assert param not in app.config
    src_value = mk_randword(8)
    app.config[param] = src_value 
    prefix = mk_randword(4) + '_'
    AppConfig(app).add_prefix_to_param_str_value(param, prefix)
    assert param in app.config
    assert app.config.get(param) == prefix + src_value

@with_setup(my_setup, my_teardown)
def test_app_config_add_prefix_to_param_dict_keys():
    app = create_app()
    param = mk_randword(8, up=True) + '_DICT'
    assert param not in app.config
    src_dict  = {mk_randword(4): mk_randword(6, up=True) for a in range(1, 5)}
    app.config[param] = src_dict.copy()
    prefix = mk_randword(4) + '_'
    AppConfig(app).add_prefix_to_param_dict_keys(param, prefix)
    assert param in app.config
    for k, v in src_dict.items():
        assert prefix + k in app.config.get(param)

