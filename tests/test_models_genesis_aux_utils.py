from nose import with_setup

from genesis_block_explorer.models.genesis.aux.utils import (
    key_id_to_wallet,
    update_dict_with_key_id,
)

def my_setup():
    pass

def my_teardown():
    pass

@with_setup(my_setup, my_teardown)
def test_update_dict_with_key_id():
    data = {
        'key_id': -2871769414074324000,
    }
    data2 = update_dict_with_key_id(data)
    assert type(data2) == dict
    assert 'key_id' in data2
    assert data2['key_id'] == str(data['key_id'])
    assert 'wallet' in data2
    assert data2['wallet'] == '1557-4974-6596-3522-7616'

    data = {
        'key_id': 4505986744193152500,
    }
    data2 = update_dict_with_key_id(data)
    assert type(data2) == dict
    assert 'key_id' in data2
    assert data2['key_id'] == str(data['key_id'])
    assert 'wallet' in data2
    assert data2['wallet'] == '0450-5986-7441-9315-2500'
