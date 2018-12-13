import logging

from sqlalchemy import func

from ..filler import Filler

from ...explicit import get_keys_model, get_ecosystem_model
from . import MemberModel

logger = logging.getLogger(__name__)

class MemberFiller(Filler):
    def __init__(self, **kwargs):
        kwargs['involved_models'] = kwargs.get('involved_models', [MemberModel])
        super(MemberFiller, self).__init__(**kwargs)
        self.context = kwargs.get('filler',
                          'MemberFiller_%s' if self.seq_num else 'MemberFiller')
        self.ecosystem_model = kwargs.get('ecosystem_model',
           get_ecosystem_model(backend_features=bc_sm.get_be_features(seq_num)))
        self.keys_model = kwargs.get('keys_model',
           get_keys_model(backend_features=bc_sm.get_be_features(seq_num)))

    def add(self, **kwargs):
        self.add_event(caller='add', stage='started')
        self.do_if_locked(**kwargs)
        self.lock(**kwargs)
        MemberModel.add_all_records_for_all_ecosystems(
            self.keys_model,
            ecosystem_model=self.ecosystem_model,
            session=self.aux_sm.get(self.seq_num),
            model_session=self.bc_sm.get(self.seq_num)
        )
        self.unlock(**kwargs)
        self.add_event(caller='add', stage='finished')
        
