from datetime import datetime

from .consts import *

def is_struct(tx):
    return tx == TxTypeFirstBlock or tx == TxTypeStopNetwork

class BaseClass(object):
    def __init__(self, classtype):
        self._type = classtype

def make_struct(name, argnames=[], BaseClass=BaseClass):
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if key not in argnames:
                raise TypeError("Argument %s not valid for %s" 
                    % (key, self.__class__.__name__))
            setattr(self, key, value)
        BaseClass.__init__(self, name[:-len("Class")])
    newclass = type(name, (BaseClass,),{"__init__": __init__})
    return newclass

class TxHeader:
    type = -1
    time = -1
    key_id = -1

    def __init__(self, **kwargs):
        self.type = kwargs.get('type', -1)
        self.time = kwargs.get('time', -1)
        self.key_id = kwargs.get('key_id', -1)

class FirstBlock:
    tx_header = None
    public_key = None
    node_public_key = None
    stop_network_cert_bundle = None

    def __init__(self, **kwargs):
        self.tx_header = kwargs.get('tx_header', None)
        self.public_key = kwargs.get('public_key', None)
        self.node_public_key = kwargs.get('node_public_key', None)
        self.stop_network_cert_bundle = kwargs.get('stop_network_cert_bundle',
                                                   None)

class StopNetwork:
    tx_header = None 
    stop_network_cert = None

    def __init__(self, **kwargs):
        self.tx_header = kwargs.get('tx_header', None)
        self.stop_network_cert = kwargs.get('stop_network_cert', None)

def get_header(obj):
    return obj.tx_header

