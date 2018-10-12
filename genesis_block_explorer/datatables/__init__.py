import six

from flask import current_app as app

from datatables import ColumnDT, DataTables

from ..utils import is_number
from ..logging import get_logger

logger = get_logger(app)

from .mixins.ext import DataTablesExtMixin
class DataTablesExt(DataTables, DataTablesExtMixin):
    pass

from .mixins.hash import DataTablesHashMixin
class DataTablesHash(DataTables, DataTablesExtMixin, DataTablesHashMixin): pass

from .mixins.time import DataTablesTimeMixin
class DataTablesTime(DataTables, DataTablesExtMixin, DataTablesTimeMixin): pass

from .mixins.hash_time import DataTablesHashTimeMixin
class DataTablesHashTime(DataTables, DataTablesExtMixin,
                         DataTablesHashTimeMixin): pass

from .mixins.hash_data import DataTablesHashDataMixin
class DataTablesHashData(DataTables, DataTablesExtMixin,
                         DataTablesHashDataMixin): pass

from .mixins.hash_data_time import DataTablesHashDataTimeMixin
class DataTablesHashDataTime(DataTables, DataTablesExtMixin,
                             DataTablesHashDataTimeMixin): pass
