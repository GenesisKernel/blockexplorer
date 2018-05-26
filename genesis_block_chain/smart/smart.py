from datetime import datetime
from random import randint 

class Contract:
    name = ""
    called = -1
    free_request = False
    tx_price = -1
    tx_gov_account = -1
    egs_rate = -1
    table_accounts = ""
    stack_cont = []
    extend = None
    block = None

def create_fake_contract_by_id(contract_id):
    return Contract(name="Fake contract",
                    called=randint(111, 999),
                    free_request==False,
                    tx_price=randint(1111, 9999),
                    tx_go_account=randint(1111111, 9999999),
                    egs_rate=randint(11, 99),
                    table_accounts="fake_table_accounts",
                    stack_cont=[],
                   ) 

def get_contract_by_id(contract_id):
    return create_fake_contract_by_id(contract_id)

