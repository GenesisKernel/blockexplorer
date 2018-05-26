from random import randint 

from .header import Header

class SmartContract(Header):
    _append_default_attrs_from_parent = True
    _default_attrs = {
        'request_id': "",
        'token_ecosystem': -1,
        'max_sum': "",
        'pay_over': "",
        'signed_by': -1,
        'data': None,
    }

    def get_parent_default_attrs(self):
        return super(SmartContract, self)._default_attrs

    def get_header_default_attrs(self):
        return self.get_parent_default_attrs()

    def get_header_attrs(self):
        return {k: getattr(self, k) for k, v in self.get_header_default_attrs().items()}

    def get_header(self):
        return Header(self.get_header_attrs())

    def get_contract_by_id(self, contract_id):
        print("get_contract_by_id contract_id: %s" % contract_id)
        from genesis_block_explorer.models.db_engine.model import (
            get_model_data_by_db_id_and_table_name
        )
        table, model, model_name \
                = get_model_data_by_db_id_and_table_name(1, '1_contracts')
        return model.query.get(contract_id).value

    def forsign(self):
        return "fake-for-sign-" + str(randint(11111, 99999))

    def __init__(self, *args, **kwargs):
        super(SmartContract, self).__init__(*args, **kwargs)
