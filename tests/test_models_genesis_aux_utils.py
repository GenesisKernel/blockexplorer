from nose import with_setup

from genesis_block_explorer.models.genesis.aux.utils import (
    key_id_to_ukey_id,
    update_dict_with_key_id,
)

def my_setup():
    pass

def my_teardown():
    pass

@with_setup(my_setup, my_teardown)
def test_key_id_to_ukey_id():
    assert key_id_to_ukey_id(-2871769414074324000) == '15574974659635227616'
    assert key_id_to_ukey_id(4505986744193152500) == '4505986744193152500'

@with_setup(my_setup, my_teardown)
def test_update_dict_with_key_id():
    data = {
        'key_id': -2871769414074324000,
    }
    data2 = update_dict_with_key_id(data)
    assert type(data2) == dict
    assert 'key_id' in data2
    assert data2['key_id'] == str(data['key_id'])
    assert 'ukey_id' in data2
    assert data2['ukey_id'] == '15574974659635227616'

    data = {
        'key_id': 4505986744193152500,
    }
    data2 = update_dict_with_key_id(data)
    assert type(data2) == dict
    assert 'key_id' in data2
    assert data2['key_id'] == str(data['key_id'])
    assert 'ukey_id' in data2
    assert data2['ukey_id'] == '4505986744193152500'
