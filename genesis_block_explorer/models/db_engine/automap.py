from sqlalchemy import (
    MetaData, ForeignKey, Column, Integer, inspect
)
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.exc import OperationalError

from dictalchemy import make_class_dictable

from ...db import db
from ...logging import get_logger
from ..utils import (
    camelize_and_dedigitize_genesis_classname,
    singular_noun_collection,
    generate_relationship_custom,
)

from .engine import (
    db_engine_to_name,
    get_discovered_db_engines,
)

logger = get_logger()

model_class_names = []

from sqlalchemy import Table, Column, Integer


import cProfile
import six
import pstats
import contextlib

@contextlib.contextmanager
def profiled():
    pr = cProfile.Profile()
    pr.enable()
    yield
    pr.disable()
    s = six.StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
    ps.print_stats()
    # uncomment this to see who's calling what
    # ps.print_callers()
    logger.info(s.getvalue())

@contextlib.contextmanager
def not_profiled():
    yield

def get_no_primary_key_table_names(app, **kwargs):
    bind_name = kwargs.get('bind_name')
    if not bind_name:
        raise Exception("bind_name isn't set")
    engine = kwargs.get('engine', None)
    if not engine:
        raise Exception("engine isn't set")
    with not_profiled():
        table_objs = []
        try:
            inspector = inspect(engine)
            for table_name in inspector.get_table_names():
                obj = {}
                pk = inspector.get_primary_keys(table_name)
                if not pk:
                    obj['table_name'] = table_name
                    obj['inspector'] = inspector
                    table_objs.append(obj)
        except OperationalError as e:
            logger.error("cant inspect engine %s" % engine)
        except Exception as e:
            raise e
    return table_objs

Model = None
Base = None
automapped_classes = {}

def add_to_automapped_classes(bind_name, class_name, cls):
    global automapped_classes
    if bind_name not in automapped_classes:
        automapped_classes[bind_name] = {}
    automapped_classes[bind_name][class_name] = cls

def import_engine_automapped_data(app, **kwargs):
    global Model, Base
    logger.debug("kwargs: %s" % kwargs)
    model_class_names = []
    engine = kwargs.get('engine', None)
    if not engine:
        raise Exception("engine isn't set")
    bind_name = kwargs.get('bind_name')
    if not bind_name:
        raise Exception("bind_name isn't set or doesn't exist in app.config")
    obj = None
    prefix = kwargs.get('class_prefix', '')
    #return (None, (None,))
    with app.app_context():
        #bind_name = 'genesis_eg1'
        with not_profiled():
            metadata = MetaData(engine)

            if kwargs.get('use_no_pk_tables', False):
                table_objs = get_no_primary_key_table_names(app,
                                                         bind_name=bind_name,
                                                         engine=engine)
                for table_obj in table_objs:
                    table_name = table_obj['table_name']
                    inspector = table_obj['inspector']
                    cols = inspector.get_columns(table_name)
                    col = cols[0]
                    c_name = col.pop('name')
                    c_type = col.pop('type')
                    col['primary_key'] = True
                    cls = Table(table_name, metadata, 
                                         Column(c_name, c_type, **col),
                                         autoload=True, extend_existing=True)
                    class_name = prefix \
                            + camelize_and_dedigitize_genesis_classname(
                                    Base, table_name, None,
                              )
                
            session = Session(engine)
            metadata.reflect(bind=engine)
            Model = declarative_base(metadata=metadata, cls=(db.Model,),
                                     bind=engine)
            Base = automap_base(metadata=metadata, declarative_base=Model)
            Base.prepare(engine, reflect=True,
                classname_for_table=camelize_and_dedigitize_genesis_classname,
                name_for_collection_relationship=singular_noun_collection,
                generate_relationship=generate_relationship_custom,
            )

        obj = Base
    
        for cls in Base.classes:
            if bind_name:
                cls.__table__.info = {'bind_key': bind_name}
                setattr(cls, '__bind_key__', bind_name)
            make_class_dictable(cls)
            class_name = prefix + cls.__name__
            model_class_names.append(class_name)
            logger.debug("Base class name: %s" % cls.__name__)
            if kwargs.get('use_automapped_classes', False):
                add_to_automapped_classes(bind_name, class_name, cls)
            else:
                globals()[class_name] = cls

    return (obj, tuple(model_class_names))

def import_automapped_data(app, **kwargs):
    model_class_names = []
    engines = get_discovered_db_engines(app)
    for bind_name, engine in engines.items(): 
        l_kwargs = kwargs
        l_kwargs['bind_name'] = bind_name
        l_kwargs['engine'] = engine
        obj, mcn = import_engine_automapped_data(app, **l_kwargs)
    return (engines, tuple(model_class_names))

