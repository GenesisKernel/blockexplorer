import six
from datetime import datetime, timezone

from .logging import get_logger

logger = get_logger()

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def semirepr(value):
    if isinstance(value, six.string_types):
        return value
    else:
        return repr(value)

def make_class_with_mixin(cls, mixin):
    table_class = cls.__table__
    tmp_cls_abstract = cls.__abstract__
    cls.__abstract__ = True
    class NewClass(cls, mixin): pass
    NewClass.__abstract__ = tmp_cls_abstract
    return NewClass

def import_attrs(dst_class, src_classes, **kwargs):
    logger.error("here")
    class CommonClassExample(object):
        pass
    common_attrs = dir(CommonClassExample)
    if not kwargs.get('multiple_src', False):
        src_classes = (src_classes,)
    for src_class in src_classes:
        for attr in dir(src_class):
            if attr not in common_attrs:
                setattr(dst_class, attr, getattr(src_class, attr))
    return dst_class

def get_backend_features_by_version(backend_version):
    if 'app' in globals():
        app = globals()['app']
    else:
        from flask import Flask
        app = Flask(__name__)
        app.config.from_pyfile('../config.py')

    if 'BACKEND_VERSION_FEATURES_MAP' not in app.config:
        return
    if backend_version not in app.config['BACKEND_VERSION_FEATURES_MAP']:
        return
    if 'features' not in \
    app.config['BACKEND_VERSION_FEATURES_MAP'][backend_version]:
        return
    return \
        app.config['BACKEND_VERSION_FEATURES_MAP'][backend_version]['features']

def ts_to_fmt_time(ts, utc=False):
    fmt = '%d/%b/%Y %H:%M:%S'
    if utc:
        return datetime.utcfromtimestamp(int(ts)).strftime(fmt)
    else:
        return datetime.fromtimestamp(int(ts)).strftime(fmt)
