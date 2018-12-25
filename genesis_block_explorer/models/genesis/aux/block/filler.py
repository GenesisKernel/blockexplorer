import logging

from sqlalchemy import func
from genesis_blockchain_api_client.errors import ServerError

from ..filler import Filler

from .....utils import is_number
from .....blockchain import (
    get_max_block_id,
    get_detailed_block,
    get_detailed_block_data,
    get_detailed_blocks,
    get_detailed_blocks_data,
)

from . import BlockModel
from .bad import BadBlockModel
from .header import HeaderModel
from ..tx import TxModel
from ..tx.param import ParamModel

logger = logging.getLogger(__name__)

class Error(Exception): pass
class FetchNumOfBlocksError(Exception): pass

class BlockFiller(Filler):
    def __init__(self, **kwargs):
        kwargs['involved_models'] = kwargs.get('involved_models',
            [BlockModel, HeaderModel, TxModel, ParamModel, BadBlockModel])
        super(BlockFiller, self).__init__(**kwargs)
        self.context = kwargs.get('filler',
                            'BlockFiller_%s' if self.seq_num else 'BlockFiller')
        self.fetch_num_of_blocks = kwargs.get('fetch_num_of_blocks', 50)
        if not is_number(self.fetch_num_of_blocks):
            raise FetchNumOfBlocksError("self.fetch_num_of_blocks: %s type(self.fetch_num_of_blocks): %s" % (self.fetch_num_of_blocks, type(self.fetch_num_of_blocks)))

    def fill_block(self, block_id, **kwargs):
        self.add_event(caller='fill_block', stage='started')
        self.do_if_locked(**kwargs)
        self.lock(**kwargs)
        #block_data = get_detailed_block_data(self.seq_num, block_id)
        try:
            BlockModel.update_from_block(
                get_detailed_block(self.seq_num, block_id),
                session=self.aux_sm.get(self.seq_num)
            )
        except ServerError as e:
            session = self.aux_sm.get(self.seq_num)
            BlockModel.add_fill_error(block_id, error=str(e),
                                      raw_error=str(e), session=session)
            session.add(BadBlockModel(id=block_id, error=str(e),
                                      raw_error=str(e)))
            session.commit()
            logger.error("Can't fetch block id: %s. Error: %s" % (block_id, e))
        self.unlock(**kwargs)
        self.add_event(caller='fill_block', stage='finished')

    def fill_blocks(self, fetch_from_block_id, fetch_to_block_id, **kwargs):
        fetch_num_of_blocks = kwargs.get('fetch_num_of_blocks',
                                         self.fetch_num_of_blocks)
        self.add_event(caller='fill_blocks', stage='started')
        self.do_if_locked(**kwargs)
        self.lock(**kwargs)
        logger.debug("BlockFiller.fill_blocks 1 fetch_from_block_id: %s fetch_to_block_id: %s" % (fetch_to_block_id, fetch_to_block_id))
        max_block_id = get_max_block_id(self.seq_num)
        if fetch_to_block_id > max_block_id:
            fetch_to_block_id = max_block_id
        fetch_to_block_id += 1
        print("fetch_from_block_id: %s fetch_to_block_id: %s fetch_num_of_blocks: %s" % (fetch_from_block_id, fetch_to_block_id, fetch_num_of_blocks))
        for from_block_id in range(fetch_from_block_id, fetch_to_block_id,
                                   fetch_num_of_blocks):
            to_block_id = fetch_to_block_id if from_block_id + fetch_num_of_blocks > fetch_to_block_id else from_block_id + fetch_num_of_blocks
            cnt = fetch_num_of_blocks if fetch_to_block_id - from_block_id > fetch_num_of_blocks else fetch_to_block_id - from_block_id
            print("from_block_id: %s to_block_id: %s cnt: %s" % (from_block_id, to_block_id, cnt))
            logger.debug("BlockFiller.fill_blocks 2 from_block_id: %s to_block_id: %s cnt: %s" % (from_block_id, to_block_id, cnt))
            try:
                BlockModel.update_from_block_set(
                    get_detailed_blocks(self.seq_num, from_block_id, cnt),
                    session=self.aux_sm.get(self.seq_num)
                )
            except ServerError as e:
                logger.error("Error: %s" % e)
                logger.info("Switching to single block fetching mode")
                for block_id in range(from_block_id, to_block_id):
                    logger.error("single block mode block_id: %s " % block_id)
                    try:
                        BlockModel.update_from_block_set(
                            get_detailed_blocks(self.seq_num, block_id, 1),
                            session=self.aux_sm.get(self.seq_num)
                        )
                    except ServerError as e:
                        session = self.aux_sm.get(self.seq_num)
                        BlockModel.add_fill_error(block_id, error=str(e),
                                                  raw_error=str(e),
                                                  session=session)
                        session.add(BadBlockModel(id=block_id, error=str(e),
                                                  raw_error=str(e)))
                        session.commit()
        self.unlock(**kwargs)
        self.add_event(caller='fill_blocks', stage='finished')

    def fill_all_blocks(self, **kwargs):
        self.add_event(caller='fill_all_blocks', stage='started')
        max_block_id = get_max_block_id(self.seq_num)
        self.fill_blocks(1, max_block_id, **kwargs)
        self.add_event(caller='fill_all_blocks', stage='finished')
        
    def update(self, **kwargs):
        updated = False
        self.add_event(caller='update', stage='started')
        self.do_if_locked(**kwargs)
        self.lock(**kwargs)
        max_block_id = get_max_block_id(self.seq_num)
        session = self.aux_sm.get(self.seq_num)
        aux_max_block_id = session.query(func.max(BlockModel.id)).scalar()
        logger.info("max_block_id: %s aux_max_block_id: %s" % (max_block_id, aux_max_block_id))
        if not aux_max_block_id:
            self.fill_all_blocks(disable_locking=True)
            updated = True
        else:
            if aux_max_block_id > max_block_id:
                self.clear(disable_locking=True)
                self.fill_all_blocks(disable_locking=True)
                updated = True
            elif aux_max_block_id < max_block_id:
                try:
                    BlockModel.update_from_block_set(
                        get_detailed_blocks(self.seq_num, aux_max_block_id + 1,
                                            max_block_id),
                        session=session
                    )
                except ServerError as e:
                    session = self.aux_sm.get(self.seq_num)
                    BlockModel.add_fill_error(block_id, error=str(e),
                                              raw_error=str(e),
                                              session=session)
                    session.add(BadBlockModel(id=block_id, error=str(e),
                                              raw_error=str(e)))
                    session.commit()
                updated = True
        self.unlock(**kwargs)
        self.add_event(caller='update', stage='finished')
        return updated

    def clear(self, **kwargs):
        self.add_event(caller='clear', stage='started')
        self.do_if_locked(**kwargs)
        self.lock(**kwargs)
        session = self.aux_sm.get(self.seq_num)
        try:
            session.query(ParamModel).delete()
            session.query(TxModel).delete()
            session.query(BlockModel).delete()
            session.query(HeaderModel).delete()
            session.commit()
        except:
            session.rollback()
        self.unlock(**kwargs)
        self.add_event(caller='clear', stage='finished')

    def stat(self, **kwargs):
        session = self.aux_sm.get(self.seq_num)
        info = {
            'max_block_id': get_max_block_id(self.seq_num),
            'aux_num_of_blocks': session.query(BlockModel.id).count(),
            'aux_max_block_id': session.query(func.max(BlockModel.id)).scalar(),
            'is_locked': self.is_locked,
        } 
        if self.is_locked:
            info['latest_lock_info'] = {
                'created_at': self.latest_lock.created_at,
                'process_id': self.latest_lock.process_id,
            }
        return info
