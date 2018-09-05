d0 = [
    {
        'id': '123',
        'txs': [
            {
                'hash': '123123',
                'contract_name': 'Contract1',
                'params': {'name1': 'val1', 'name2': 'val2'},
                'key_id': '123123123',
            },
            {
                'hash': '123456',
                'contract_name': 'Contract2',
                'params': {'name3': 'val3', 'name4': 'val4'},
                'key_id': '123123456',
            }
        ]
    },
    {
        'id': '456',
        'txs': [
            {
                'hash': '456456',
                'contract_name': 'Contract3',
                'params': {'name5': 'val5', 'name6': 'val6'},
                'key_id': '456456456',
            },
            {
                'hash': '456789',
                'contract_name': 'Contract4',
                'params': {'name6': 'val6', 'name7': 'val7'},
                'key_id': '456456789',
            }
        ]
    },
]

d1 = [
    {
        '123': [
            {
                'Hash': '123123',
                'ContractName': 'Contract1',
                'Params': {'ParamName1': 'val1', 'ParamName2': 'val2'},
                'KeyID': '123123123',
            },
            {
                'Hash': '123456',
                'ContractName': 'Contract2',
                'Params': {'ParamName3': 'val3', 'ParamName4': 'val4'},
                'KeyID': '123123456',
            }
        ]
    },
    {
        '456': [
            {
                'Hash': '456456',
                'ContractName': 'Contract3',
                'Params': {'ParamName5': 'val5', 'ParamName6': 'val6'},
                'KeyID': '456456456',
            },
            {
                'Hash': '456789',
                'ContractName': 'Contract4',
                'Params': {'ParamName6': 'val6', 'ParamName7': 'val7'},
                'KeyID': '456456789',
            }
        ]
    },
]

def blocks_list_to_dict(l):
    _dict = {}
    for d in l:
        block_id = tuple(d.keys())[0]
        _dict[block_id] = d[block_id]
    return _dict

d2 = blocks_list_to_dict(d1)

d3 = [
    {
        '123': {
            'header': {
                'block_id': '123',
                'time': 1535819403,
                'ecosystem_id': 0,
                'node_position': 0,
                'sign': '6LVsJppg6jPGYv/wpfvz+/9+Cc44POXMWAFcOFB60BKT06tg7S2R4WEcxcWQmRVesyanT8y/5XETsnzOgBDMIA==', # e8b56c269a60ea33c662fff0a5fbf3fbff7e09ce383ce5cc58015c38507ad01293d3ab60ed2d91e1611cc5c59099155eb326a74fccbfe57113b27cce8010cc20
                'hash': "kQPWd2asxbCDTuBZtAEDSNrV6emBb4ILLsvuTqRVoqc=", # 9103d67766acc5b0834ee059b4010348dad5e9e9816f820b2ecbee4ea455a2a7
                'version': 1,
            },
            'hash': '3JY6NL6KiuMGXgdzSmnHKPnhwZzAjFThiaHtkJekZdI=', # dc963a34be8a8ae3065e07734a69c728f9e1c19cc08c54e189a1ed9097a465d2 
            'ecosystem_id': 0,
            'node_position': 0,
            'key_id': -5953874702473585171,
            'tx_count': 2,
            'time': 1535819403,
            'rollbacks_hash': 'leECi3/aNz4Hkk7AFUJ9bAjsdOYjGMY0+/ZpspzWgAI=', # 95e1028b7fda373e07924ec015427d6c08ec74e62318c634fbf669b29cd68002
            'mrkl_root': "N2U2NmMwNjkxMzc2NDAxYTA4ZGQ2YWUzMGMyMDVlOTgxYWI1OTYxMDRiYzcyMDhlOTM5NjI3ODVkYWE5ZDQ4Nw==", #  b"7e66c0691376401a08dd6ae30c205e981ab596104bc7208e93962785daa9d487" # 7e66c0691376401a08dd6ae30c205e981ab596104bc7208e93962785daa9d487 # 37653636633036393133373634303161303864643661653330633230356539383161623539363130346263373230386539333936323738356461613964343837
            'bin_data': None,
            'sys_update': False,
            'gen_block': False,
            'stop_count': 0,
            'transactions': [
                {
                    'hash': '123123',
                    'contract_name': 'Contract1',
                    'params': {'ParamName1': 'val1', 'ParamName2': 'val2'},
                    'key_id': '123123123',
                    'time': 123123123,
                },
                {
                    'hash': '123456',
                    'contract_name': 'Contract2',
                    'params': {'ParamName3': 'val3', 'ParamName4': 'val4'},
                    'key_id': '123123456',
                    'time': 123123456,
                }
            ],
        },
    },
    {
        '456': {
            'header': {
                'block_id': '456',
                'time': 123123123,
                'ecosystem_id': 0,
                'node_position': 0,
                'sign': '6LVsJppg6jPGYv/wpfvz+/9+Cc44POXMWAFcOFB60BKT06tg7S2R4WEcxcWQmRVesyanT8y/5XETsnzOgBDMIA==',
                'hash': None,
                'version': 1,
            },
            'hash': '3JY6NL6KiuMGXgdzSmnHKPnhwZzAjFThiaHtkJekZdI=',
            'ecosystem_id': 0,
            'node_position': 0,
            'key_id': -5953874702473585171,
            'tx_count': 2,
            'time': 1535819403,
            'rollbacks_hash': 'leECi3/aNz4Hkk7AFUJ9bAjsdOYjGMY0+/ZpspzWgAI=',
            'mrkl_root': "N2U2NmMwNjkxMzc2NDAxYTA4ZGQ2YWUzMGMyMDVlOTgxYWI1OTYxMDRiYzcyMDhlOTM5NjI3ODVkYWE5ZDQ4Nw==",
            'bin_data': None,
            'sys_update': False,
            'gen_block': False,
            'stop_count': 0,
            'transactions': [
                {
                    'hash': '456456',
                    'contract_name': 'Contract3',
                    'params': {'ParamName5': 'val5', 'ParamName6': 'val6'},
                    'key_id': '456456456',
                    'time': 456456456,
                },
                {
                    'hash': '456789',
                    'contract_name': 'Contract4',
                    'params': {'ParamName6': 'val6', 'ParamName7': 'val7'},
                    'key_id': '456456789',
                    'time': 456456789,
                }
            ],
        }
    },
]

d4 = blocks_list_to_dict(d3)

def get_txs(d):
    return d[tuple(d.keys())[0]]

