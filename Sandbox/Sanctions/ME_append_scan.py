
import settings
import pyodbc
import json
import os
from ME_Append import get_me_nbr
from MarkLogicConnection import MarkLogicConnection


def get_state(uri):
    # example - '/json/2019.10.30_OH_NA_SL/schwartz_2172.json'
    _sl_index = uri.index('_SL/')
    return uri[_sl_index - 5:_sl_index - 3]

auth_aims = os.environ.get('auth_aims')
aims_user, aims_pass = (auth_aims.split())
AIMS_conn = pyodbc.connect('DSN=aims_prod; UID={}; PWD={}'.format(aims_user, aims_pass))
AIMS_conn.execute('SET ISOLATION TO DIRTY READ;')

"""
from datalabs.access.database import Database
from datalabs.access.credentials import Credentials

credentials = Credentials.load(...)
"""
auth_marklogic = os.environ.get('auth_marklogic_dev')
ml_user, ml_pass = (auth_marklogic.split())

MarkLogicCon = MarkLogicConnection(username=ml_user,
                                   password=ml_pass,
                                   server='prod')

# Get all URIs
metadata_uris = MarkLogicCon.get_file_uris()  # default params: database='PhysicianSanctions', collection='json_data'

# remove Summary List files
metadata_uris = [f for f in metadata_uris if 'summarylist' not in f]

# scan all files
for uri in metadata_uris:
    # download the json file for this URI
    json_data = json.loads(MarkLogicCon.get_file(uri=uri))

    me_nbr = json_data['sanction']['physician']['me']

    # if ME is filled, we don't need to do anything
    if me_nbr in ['None', None, 'Null', 'none', 'null', 'NA', 'na', '']:
        # ME number not filled

        # if license is filled, we can perform a search for ME number
        lic_nbr = json_data['sanction']['physician']['license']

        if lic_nbr not in ['None', None, 'Null', 'none', 'null', '']:
            # license number is complete
            # searching for ME number
            first = json_data['sanction']['physician']['name_first']
            last = json_data['sanction']['physician']['name_last']
            state = get_state(uri)
            me_nbr = get_me_nbr(first=first, last=last, state=state, lic_nbr=lic_nbr, con=AIMS_conn)

            if me_nbr is not None:
                # updating file
                MarkLogicCon.set_me_nbr(uri=uri, me_nbr=me_nbr)
