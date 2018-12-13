from nose import with_setup

from genesis_block_explorer.utils import (
    cmp_lists_to_update_first,
)

def my_setup():
    pass

def my_teardown():
    pass

@with_setup(my_setup, my_teardown)
def test_cmp_lists_to_update_first():
    one = [-10, 13, 8, 5]
    two = [-10, 3, 8, 6]
    res = cmp_lists_to_update_first(one, two)
    assert type(res) == dict
    assert 'to_delete' in res
    assert 'to_add' in res
    assert res['to_delete'] == {13, 5}
    assert res['to_add'] == {3, 6}
