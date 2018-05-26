from ..helpers.objects import SimpleAttrDictPlus


class BlockExtraData(SimpleAttrDictPlus):
    _default_attrs = {
        'key_id_len': -1,
        'offset': -1,
        'sign_size': -2,
        'sign_bin': None,
    }

    def __init__(self, *args, **kwargs):
        super(BlockExtraData, self).__init__(*args, **kwargs)


class BlockData(SimpleAttrDictPlus):
    _default_attrs = {
        'block_id': -1,
        'time': -1,
        'ecosystem_id': -1,
        'key_id': -1,
        'node_position': -1,
        'sign': None,
        'block_hash': None,
        'version': -1,
        'extra': None,
    }

    def __init__(self, *args, **kwargs):
        super(BlockData, self).__init__(*args, **kwargs)

