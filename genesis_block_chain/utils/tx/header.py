from ...helpers.objects import SimpleAttrDictPlus

class Header(SimpleAttrDictPlus):
    _default_attrs = {
        'type': -1,
        'time': -1,
        'ecosystem_id': -1,
        'key_id': -1,
        'role_id': -1,
        'network_id': -1,
        'node_position': -1,
        'public_key': None,
        'bin_signatures':  None,
    }

    def __init__(self, *args, **kwargs):
        super(Header, self).__init__(*args, **kwargs)
