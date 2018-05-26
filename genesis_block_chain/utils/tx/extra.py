from ...helpers.objects import SimpleAttrDictPlus

class Extra(SimpleAttrDictPlus):
    _default_attrs = {
        'size': -1,
        'size_offset': -1,
        'raw': None,
    }

    def __init__(self, *args, **kwargs):
        super(Extra, self).__init__(*args, **kwargs)

