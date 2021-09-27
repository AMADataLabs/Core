"""OneView Static Reference Data"""
provider_affiliation_group = {
    'id': ['ATT', 'ADM', 'LTC'],
    'description': ['Attending', 'Admitting', 'Long Term Care']
}

provider_affiliation_type = {
    'id': [1, 2, 3, 4, 5, 6, 7, 8],
    'description': ['Attending', 'IDN Affiliated', 'Admitting', 'Staff', 'Consulting', 'Treating',
                    'IDN Affiliated (Inferred)', 'Admitting (Inferred)']
}

profit_status = {
    'id': ['For Profit', 'Not For Profit', 'Government'],
    'description': ['For Profit', 'Not For Profit', 'Government']
}

owner_status = {
    'id': ['INDEPENDENT', 'NOT INDEPENDENT'],
    'description': ['Independent', 'Not Independent']
}

tables = [provider_affiliation_group, provider_affiliation_type, profit_status, owner_status]
