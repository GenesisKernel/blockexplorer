import six
import os

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def is_string(s):
    return isinstance(s, six.string_types)

