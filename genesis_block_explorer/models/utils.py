import re
import inflect
from pprint import pprint

p = inflect.engine()

def camelize_classname(base, tablename, table):
    "Produce a 'camelized' class name, e.g. "
    "'words_and_underscores' -> 'WordsAndUnderscores'"
    return str(tablename[0].upper() + \
            re.sub(r'_([a-z])', lambda m: m.group(1).upper(), tablename[1:]))

def camelize_and_dedigitize_classname(base, tablename, table, prefix="C"):
    "Produce a 'camelized' class name, e.g. "
    "'words_and_underscores' -> 'WordsAndUnderscores'"
    "If a class name first letter is a digit it will be prefixed:"
    "'1_blocks' -> 'C1Blocks' for default prefix"
    if tablename[0].isdigit():
        begin = prefix + tablename[0]
    else:
        begin = tablename[0].upper()
    return str(begin + \
            re.sub(r'_([a-z])', lambda m: m.group(1).upper(), tablename[1:]))

def camelize_and_dedigitize_genesis_classname(base, tablename, table):
    return camelize_and_dedigitize_classname(base, tablename, table,
                                             prefix="Es")

def camelize_and_singular_noun_classname(base, tablename, table):
    "Produce a 'camelized' class name, e.g. "
    "'words_and_underscores' -> 'WordsAndUnderscore'"
    print("tablename orig: " + str(tablename))
    try:
        tablename = p.singular_noun(tablename)
    except:
        pass
    print("tablename after: " + str(tablename))
    return str(tablename[0].upper() + \
            re.sub(r'_([a-z])', lambda m: m.group(1).upper(), tablename[1:]))

def pluralize_collection(base, local_cls, referred_cls, constraint):
    "Produce an 'uncamelized', 'pluralized' class name, e.g. "
    "'SomeTerm' -> 'some_terms'"

    referred_name = referred_cls.__name__
    uncamelized = re.sub(r'[A-Z]',
                         lambda m: "_%s" % m.group(0).lower(),
                         referred_name)[1:]
    pluralized = p.plural(uncamelized)
    return pluralized

def singular_noun_collection(base, local_cls, referred_cls, constraint):
    "Produce an 'uncamelized', 'pluralized' class name, e.g. "
    "'SomeTerm' -> 'some_term'"

    referred_name = referred_cls.__name__
    uncamelized = re.sub(r'[A-Z]',
                         lambda m: "_%s" % m.group(0).lower(),
                         referred_name)[1:]
    return uncamelized

def singular_noun_with_collection_word(base, local_cls, referred_cls, constraint):
    "Produce an 'uncamelized', 'pluralized' class name, e.g. "
    "'SomeTerm' -> 'some_term'"

    referred_name = referred_cls.__name__
    uncamelized = re.sub(r'[A-Z]',
                         lambda m: "_%s" % m.group(0).lower(),
                         referred_name)[1:]
    return uncamelized + '_collection'

def name_for_scalar_relationship(base, local_cls, referred_cls, constraint):
    name = referred_cls.__name__.lower()
    local_table = local_cls.__table__
    if name in local_table.columns:
        newname = name + "_"
        return newname
    return name

def name_for_collection_relationship(base, local_cls, referred_cls, constraint):
    name = referred_cls.__name__.lower() + '_collection'
    for c in referred_cls.__table__.columns:
        if c == name:
            name += "_"
    return name

def generate_relationship_custom(base, direction, return_fn, attrname, local_cls, referred_cls, **kw):
    from sqlalchemy.orm import relationship, backref
    if return_fn is backref:
        if attrname == 'address':
            kw['uselist'] = False
        return return_fn(attrname, **kw)
    elif return_fn is relationship:
        return return_fn(referred_cls, **kw)
    else:
        raise TypeError("Unknown relationship function: %s" % return_fn)
