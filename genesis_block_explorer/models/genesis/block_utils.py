from decimal import Decimal
import re
import collections

from ...utils import ts_to_fmt_time

class Error(Exception):
    pass

class Item:

    def __init__(self, name, value, **kwargs):
        """
        Source:
            u - undef; m - manual; d - database; b - block
        Raw:
            0 - false; 1 - true
        Type:
            b   - bool; str; int; dec - decimal
            ts  - timestamp; tf  - time formatted
        """
        self._item_type = 'Item'
        self.name  = name
        self.value = value
        a = kwargs.get('a', "")
        self.title = kwargs.get('t', self.name)

        a = a.split(" ")
        self.src = a[0]
        if a[1] == 0 or a[1] == '0' or a[1] == 'true' or a[1] == 'True':
            self.raw = False
        else:
            self.raw = True
        self.type = a[2]
        if not self.raw:
            if self.type == 'str':
                self.value = str(self.value)
            elif self.type == 'int':
                self.value = int(self.value)
            elif self.type == 'dec':
                self.value = Decimal(self.value)
            elif self.type == 'hex':
                self.value = self.value.hex()


class BlockItem(Item):

    def print(self):
        print("name: %s src: %s raw: %s type: %s value: %s title: %s db_id: %d block_id: %d" % (self.name, self.src, self.raw, self.type, self.value, self.title, self.db_id, self.block_id))

    def to_dict(self):
        return dict(name=self.name, src=self.src,
                             raw=self.raw, type=self.type,
                             value=self.value, title=self.title,
                             db_id=self.db_id, block_id=self.block_id)

    def __init__(self, *args, **kwargs):
        super(BlockItem, self).__init__(*args, **kwargs)
        self.db_id = kwargs.get('db_id', 1)
        self.block_id = kwargs.get('block_id', 1)
        self._item_type = 'BlockItem'


class TxItem(Item):

    def print(self):
        print("name: %s src: %s raw: %s type: %s value: %s title: %s db_id: %d tx_hash : %s" % (self.name, self.src, self.raw, self.type, self.value, self.title, self.db_id, self.tx_hash))

    def to_dict(self):
        return dict(name=self.name, src=self.src,
                             raw=self.raw, type=self.type,
                             value=self.value, title=self.title,
                             db_id=self.db_id, tx_hash=self.tx_hash)

    def __init__(self, *args, **kwargs):
        super(TxItem, self).__init__(*args, **kwargs)
        self.db_id = kwargs.get('db_id', 1)
        self.tx_hash = kwargs.get('tx_hash', '')
        self._item_type = 'TxItem'

class BlockTxItem(Item):

    def print(self):
        print(str(self))
        #print("name: %s src: %s raw: %s type: %s value: %s title: %s db_id: %d block_id: %s" % (self.name, self.src, self.raw, self.type, self.value, self.title, self.db_id, self.block_id))

    def to_dict(self):
        return dict(db_id=self.db_id, block_id=self.block_id,
                    hash=self.hash, contract_name=self.contract_name,
                    params=self.params, key_id=self.key_id)

    def __init__(self, *args, **kwargs):
        super(BlockTxItem, self).__init__(*args, **kwargs)
        self.db_id = kwargs.get('db_id', 1)
        self.block_id = kwargs.get('block_id', '')
        self.hash = kwargs.get('hash', '')
        self.contract_name = kwargs.get('contract_name', '')
        self.params = kwargs.get('params', '')
        self.key_id = kwargs.get('key_id', '')
        self._item_type = 'BlockTxItem'



class ItemCreationError(Error):
    pass

class NoBlockData(ItemCreationError):
    pass

class NoTxInfo(ItemCreationError):
    pass

class NoSuchAttr(ItemCreationError):
    pass

class NoSuchKey(ItemCreationError):
    pass

# p.name
class PAttr(BlockItem):
    def __new__(cls, name, p, **kwargs):
        value = None
        if hasattr(p, name):
            value = getattr(p, name)
            return BlockItem(name, value, **kwargs)
        else:
            return NoSuchAttr(name)

# p.tx_name
class PTxAttr(BlockItem):
    def __new__(cls, name, p, **kwargs):
        name = "tx_" + name
        value = None
        if hasattr(p, name):
            value = p.name
            return BlockItem(name, value, **kwargs)
        else:
            return NoSuchKey(name)

# p.block_data[name]
class PBDKey(BlockItem):
    def __new__(cls, name, p, **kwargs):
        value = None
        if hasattr(p, 'block_data'):
            if name in p.block_data:
                value = p.block_data[name]
                return BlockItem(name, value, **kwargs)
            else:
                return NoSuchKey(name)
        else:
            return NoBlockData()

# p.tx_smart[name]
class PTxSmartKey(BlockItem):
    def __new__(cls, name, p, **kwargs):
        value = None
        if hasattr(p, 'tx_smart'):
            m = re.search('^(tx_)?(.*)$', name)
            if m:
                dst_name = m.group(2)
            else:
                dst_name = name
            if dst_name in p.tx_smart:
                value = p.tx_smart[dst_name]
                return BlockItem(name, value, **kwargs)
            else:
                return NoSuchKey(name)
        else:
            return NoTxInfo()

# p.tx_extra[name]
class PTxExtraKey(BlockItem):
    def __new__(cls, name, p, **kwargs):
        value = None
        if hasattr(p, 'tx_extra'):
            m = re.search('^(tx_)?(.*)$', name)
            if m:
                dst_name = m.group(2)
            else:
                dst_name = name
            if dst_name in p.tx_extra:
                value = p.tx_extra[dst_name]
                return BlockItem(name, value, **kwargs)
            else:
                return NoSuchKey(name)
        else:
            return NoTxInfo()


def create_time_items(item_cls, name, value, a_s="", t=""): 
    ts = item_cls(name, value, a=a_s+" 1 ts", t="Raw "+t+" (Timestamp)")
    try:
        raise ts    
    except ItemCreationError as e:
        return (ts, ts, ts)
    except TypeError:
        pass
    loc = item_cls(name+"_local", ts_to_fmt_time(ts.value, utc=False),
                   a=a_s+" 0 tf", t=t+" (Local)")
    utc = item_cls(name+"_utc", ts_to_fmt_time(ts.value, utc=True),
                   a=a_s+" 0 tf", t=t+" (UTC)")
    return (ts, loc, utc)


class Rows:

    def to_list_of_dicts(self):
        data = []
        for i in self.data:
            print("i: %s" % i.to_dict()) #i.print()
            data.append(i.to_dict())
        return data

    def print(self):
        for i in self.data:
            i.print()


class TransactionRows(Rows):

    def __init__(self, **kwargs):
        self.db_id = kwargs.get('db_id', 1)
        self.tx_hash = kwargs.get('tx_hash', '')
        self.data = []

    def add(self, i):
        try:
            raise i    
        except ItemCreationError as e:
            return 
        except TypeError:
            pass
        i.db_id = self.db_id
        i.tx_hash = self.tx_hash
        self.data.append(i)

class BlockTransactionRows(Rows):

    def __init__(self, **kwargs):
        self.db_id = kwargs.get('db_id', 1)
        self.block_id = kwargs.get('block_id', '')
        self.data = []

    def add(self, i):
        try:
            raise i    
        except ItemCreationError as e:
            return 
        except TypeError:
            pass
        i.db_id = self.db_id
        i.block_id = self.block_id
        self.data.append(i)

class BlockRows(Rows):

    def __init__(self, **kwargs):
        self.db_id = kwargs.get('db_id', 1)
        self.block_id = kwargs.get('block_id', 1)
        self.data = []

    def consolidate(self):
        up_data = collections.OrderedDict()
        for i in self.data:
            up_data[i.name] = i
        up_data2 = []
        for k, v in up_data.items():
            up_data2.append(v)
        self.data = up_data2

    def add(self, i):
        try:
            raise i    
        except ItemCreationError as e:
            return 
        except TypeError:
            pass
        i.db_id = self.db_id
        i.block_id = self.block_id
        self.data.append(i)


