import logging
import datetime
import time

from celery.task.base import periodic_task
from socketIO_client import SocketIO, BaseNamespace

from tcpping import tcpping

from . import celery, application

from ..models.genesis.aux.config import (
    update_aux_db_engine_discovery_map
)
from ..models.genesis.aux.block.filler import BlockFiller
from ..models.genesis.aux.config import get_num_of_backends

logger = logging.getLogger(__name__)

class Error(Exception): pass
class TCPPortIsNotAvailableError(Error): pass
class AuxNamespace(BaseNamespace): pass

@celery.task
def filler_test_add(x, y):
    time.sleep(10)
    return x + y

def block_filler_update(seq_num):
    logger.debug("starting block filler update for seq_num: %s" % seq_num)
    bf = BlockFiller(app=application, seq_num=seq_num,
        fetch_num_of_blocks=application.config.get('FETCH_NUM_OF_BLOCKS'))
    result = bf.update()
    logger.debug("result: %s" % result)
    if result:
        host = application.config.get('SOCKETIO_HOST', '127.0.0.1')
        port = application.config.get('SOCKETIO_PORT', 5000)
        timeout = 1
        if tcpping(host=host, port=port, timeout=timeout):
            socketIO = SocketIO(host, port)
            aux_namespace = socketIO.define(AuxNamespace, '/backend%d' \
                    % seq_num)
            aux_namespace.emit('my_broadcast_event', {"data": "reload"})
            socketIO.wait(seconds=timeout)
        else:
            raise TCPPortIsNotAvailableError("%s: %s, timeout: %d" \
                    % (host, port, timeout))
    return result

@celery.task(soft_time_limit=30)
def block_filler_update_task(seq_num):
    return block_filler_update(seq_num)

def block_filler_clear(seq_num):
    bf = BlockFiller(app=application, seq=num,
        fetch_num_of_blocks=application.config.get('FETCH_NUM_OF_BLOCKS'))
    return bf.clear()

@celery.task
def block_filler_clear_task(seq_num):
    block_filler_clear(seq_num)

def run_block_fillers_updates():
    results = []
    for seq_num in range(1, get_num_of_backends(application) + 1):
        logger.debug("running update for seq_num: %s" % seq_num)
        bf = BlockFiller(app=application, seq_num=seq_num,
            fetch_num_of_blocks=application.config.get('FETCH_NUM_OF_BLOCKS'))
        #time.sleep(1)
        results.append(bf.update())
    return results

def run_async_block_fillers_updates():
    async_results = []
    for seq_num in range(1, get_num_of_backends(application) + 1):
        async_results.append(block_filler_update_task.apply_async((seq_num,)))
    return async_results 

#@periodic_task(run_every=datetime.timedelta(seconds=1))
#def periodic_run_block_fillers_update_task():
#    run_block_fillers_updates()

@periodic_task(run_every=datetime.timedelta(seconds=1), soft_time_limit=30)
def periodic_run_async_block_fillers_update_task():
    run_async_block_fillers_updates()

