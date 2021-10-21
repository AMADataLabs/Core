"""OneView Static Reference Data"""
provider_affiliation_group = {
    'id': ['ATT', 'ADM', 'LTC', 'UNKNOWN'],
    'description': ['Attending', 'Admitting', 'Long Term Care', 'Unknown']
}


provider_affiliation_type = {
    'id': [1, 2, 3, 4, 5, 6, 7, 8, 0],
    'description': ['Attending', 'IDN Affiliated', 'Admitting', 'Staff', 'Consulting', 'Treating',
                    'IDN Affiliated (Inferred)', 'Admitting (Inferred)', 'Unknown']
}


profit_status = {
    'id': ['For Profit', 'Not for Profit', 'Government', 'UNKNOWN'],
    'description': ['For Profit', 'Not For Profit', 'Government', 'Unknown']
}


owner_status = {
    'id': ['INDEPENDENT', 'NOT INDEPENDENT', 'ALLIED', 'UNKNOWN'],
    'description': ['Independent', 'Not Independent', 'Allied', 'Unknown']
}


fips_supplement = dict(
    id=['70030', '64002', '64005', '64040', '64060', '     '],
    state=['70', '64', '64', '64', '64', '  '],
    county=['030', '002', '005', '040', '060', '   '],
    description=[
        'Koror, Palau',
        'Chuuk, Federated States of Micronesia',
        'Kosrae, Federated States of Micronesia',
        'Pohnpei, Federated States of Micronesia',
        'Yap, Federated States of Micronesia',
        'Unknown/Not Specified'
    ]
)


tables = [provider_affiliation_group, provider_affiliation_type, profit_status, owner_status]
