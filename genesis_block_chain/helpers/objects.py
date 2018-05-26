from attrdict import AttrDict

class SimpleAttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(SimpleAttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self


class GetUpdateAttrsMixin:
    attrs_excludes = ['attrs_excludes', '__module__', '__getattr__',
                      '__init__', '__dict__', '__weakref__', '__doc__']
    @classmethod
    def get_attrs(cls):
        return dict(filter(lambda x: x, [None if k in cls.attrs_excludes else (k,v) for k, v in cls.__dict__.items()]))

    def update_from_attrs(self):
        for k, v in self.get_attrs().items():
            self[k]=v


class AttrDictGetUpdateAttrsMixin(GetUpdateAttrsMixin):
    attrs_excludes = ['attrs_excludes', '__module__', '__getattr__',
                      '__init__', '__dict__', '__weakref__', '__doc__',
                      '__abstractmethods__', '_abc_registry', '_abc_cache',
                      '_abc_negative_cache', '_abc_negative_cache_version']


class UpdateAttrsFromDictMixin:
    def update_attrs_from_dict(self, src_dict, **kwargs):
        if kwargs.get('strict', True):
            dst_key_prefix = kwargs.get('dst_key_prefix', False)
            if dst_key_prefix:
                [setattr(self, dst_key_prefix + k, v) \
                        if hasattr(self, dst_key_prefix + k) \
                        else None for k, v in src_dict.items()]
            else:
                [setattr(self, k, v) if hasattr(self, k) else None \
                        for k, v in src_dict.items()]
        else:
            self.__dict__.update(src_dict)


class DefaultAttrsMixin:
    _update_attrs_strict = True
    _default_attrs = {}

    @classmethod
    def get_default_attrs(cls):
        return cls._default_attrs

    def get_attrs(self):
        return {k: getattr(self, k) for k in self._default_attrs.keys()}

    def get_parent_default_attrs(self):
        return super(DefaultAttrsMixin, self)._default_attrs

    @classmethod 
    def update_from_default_attrs(cls):
        [setattr(cls, k, v) for k, v in cls._default_attrs.items()]

    def update_from_default_attrs(self, *args, **kwargs):
        if args:
            in_attrs = args[0]
        else:
            in_attrs = {}
        in_attrs.update(kwargs)
        attrs = dict(self.get_default_attrs())
        if self._update_attrs_strict:
            keys = attrs.keys()
            filtered = {k: v for k, v in in_attrs.items() if k in keys}
            attrs.update(filtered)
        else:
            attrs.update(in_attrs)
        [setattr(self, k, v) for k, v in attrs.items()]


class AttrDictPlus(AttrDict, DefaultAttrsMixin, UpdateAttrsFromDictMixin):
    def __init__(self, *args, **kwargs):
        self.update_from_default_attrs()
        super(AttrDictPlus, self).__init__(*args, **kwargs)


class SimpleAttrDictPlus(SimpleAttrDict, DefaultAttrsMixin, UpdateAttrsFromDictMixin):
    _append_default_attrs_from_parent = False

    def get_orig_attrs(self):
        return {k: getattr(self, k) for k in self._default_attrs.keys() if k not in self.get_parent_default_attrs().keys()}

    def get_orig_default_attrs(self):
        return {k: self._default_attrs[k] for k in self._default_attrs.keys() if k not in self.get_parent_default_attrs().keys()}

    def __init__(self, *args, **kwargs):
        if self._append_default_attrs_from_parent:
            self._default_attrs.update(self.get_parent_default_attrs())
        if args:
            in_attrs = args[0]
        else:
            in_attrs = {}
        in_attrs.update(kwargs)
        if self._update_attrs_strict:
            attrs = dict(self.get_default_attrs())
            keys = attrs.keys()
            filtered = {k: v for k, v in in_attrs.items() if k in keys}
            super(SimpleAttrDictPlus, self).__init__(*args, **filtered)
            self.update_from_default_attrs(*args, **filtered)
        else:
            super(SimpleAttrDictPlus, self).__init__(*args, **in_attrs)
            self.update_from_default_attrs(*args, **in_attrs)


class TestSimpleAttrDictPlus(SimpleAttrDictPlus):
    _default_attrs = {
        'one': 1,
        'two': 2,
    }
    def __init__(self, *args, **kwargs):
        super(TestSimpleAttrDictPlus, self).__init__(*args, **kwargs)


class TestSimpleAttrDictPlusChild(TestSimpleAttrDictPlus):
    _append_default_attrs_from_parent = True
    _default_attrs = {
        'three': 3,
        'four': 4,
    }

    def get_parent_default_attrs(self):
        return super(TestSimpleAttrDictPlusChild, self)._default_attrs

    def __init__(self, *args, **kwargs):
        super(TestSimpleAttrDictPlusChild, self).__init__(*args, **kwargs)


