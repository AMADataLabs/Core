import json
import os
import pandas as pd
import jaydebeapi
from datalabs.access.ml_sanctions import MarkLogicConnection
import settings


class SanctionsMEScan:
    def __init__(self, server):
        self._marklogic_username = None
        self._marklogic_password = None
        self._aims_source_name = None
        self._aims_username = None
        self._aims_password = None

        self._marklogic_con = None
        self._server = server
        self._aims_con = None

    def _set_environment_variables(self):
        self._marklogic_username = os.environ.get('CREDENTIALS_MARKLOGIC_USERNAME')
        self._marklogic_password = os.environ.get('CREDENTIALS_MARKLOGIC_PASSWORD')
        self._aims_source_name = os.environ.get('DATABASE_NAME_AIMS')
        self._aims_username = os.environ.get('CREDENTIALS_AIMS_USERNAME')
        self._aims_username = os.environ.get('CREDENTIALS_AIMS_PASSWORD')

    def _set_database_connections(self):
        self._marklogic_con = MarkLogicConnection(username=self._marklogic_username,
                                                  password=self._marklogic_password,
                                                  server=self._server)

        self._aims_con = jaydebeapi.connect(
            'com/informix/jdbc/IfxConnection',
            'jdbc:informix-sqli://rdbp1627.ama-assn.org:22093/aims_prod:informixserver=prd1srvxnet',
            [self._aims_username, self._aims_password],
            './jdbc-4.50.2.fix-1.jar')

        self._aims_con.cursor().execute('SET ISOLATION TO DIRTY READ;')

    @classmethod
    def _get_state(cls, uri: str):
        # example - '/json/2019.10.30_OH_NA_SL/schwartz_2172.json'
        _sl_index = uri.index('_SL/')
        return uri[_sl_index - 5:_sl_index - 3]

    def _scan_uris(self, uris: list):
        """
        Scans MarkLogic for metadata files specified by a list of uris. If the metadata file is eligible for
        an ME lookup (license number populated, ME nbr NOT populated,
        :param uris: list of MarkLogic document URIs--sanction metadata files--to scan
        :return: None
        """
        uris = [f for f in uris if 'summarylist' not in f]  # remove Summary List files
        for uri in uris:
            # download the json file for this URI
            json_data = json.loads(self._marklogic_con.get_file(uri=uri))
            me_nbr = json_data['sanction']['physician']['me']

            # if ME not entered, it may be eligible for a ME search
            if me_nbr in ['None', None, 'Null', 'none', 'null', 'NA', 'na', '']:

                # if license is filled, we can perform a search for ME number
                lic_nbr = json_data['sanction']['physician']['license']

                if lic_nbr not in ['None', None, 'Null', 'none', 'null', '']:
                    # license number is entered
                    first = json_data['sanction']['physician']['name_first']
                    last = json_data['sanction']['physician']['name_last']
                    state = self._get_state(uri)
                    if first is not None and last is not None:
                        me_nbr = self._get_me_nbr(first=first,
                                                  last=last,
                                                  state=state,
                                                  lic_nbr=lic_nbr)
                        if me_nbr is not None:
                            # updating file
                            self._marklogic_con.set_me_nbr(uri=uri, json_file=json_data, me_nbr=me_nbr)

    def _get_me_nbr(self, first, last, state, lic_nbr):
        """
        initial search is just on first + last because I was getting some weird errors / unexpected behavior when
        using state_cd to compare to state in the SQL query. Final matching on state and license number are done
        once the initial results are in a DataFrame.
        """
        sql_template = \
            """
            SELECT 
                ek.key_type_val,
                nm.first_nm,
                nm.last_nm,
                lic.lic_nbr,
                lic.state_cd

            FROM
                person_name_et nm

                INNER JOIN
                entity_key_et ek
                ON nm.entity_id = ek.entity_id

                INNER JOIN
                license_lt lic
                ON lic.entity_id = ek.entity_id

            WHERE
                ek.key_type          = "ME"    AND
                UPPER(nm.first_nm)   = "{}"    AND
                UPPER(nm.last_nm)    = "{}"
            ;
            """

        sql = sql_template.format(first.upper(), last.upper())
        data = pd.read_sql(con=self._aims_con, sql=sql)

        # sometimes the license number in our databases has a prefix, "MD" or "DO" to designate license type.
        # to be flexible with unknown prefixes/suffixes, I just look to see if our license number contains the target.
        data = data[
            (data['state_cd'] == state) & (data['lic_nbr'].apply(lambda x: str(lic_nbr) in x))].drop_duplicates()

        # we should only have one result at this point--duplicates on name + state + license should be impossible
        if len(data) == 1:
            return data['key_type_val'].apply(str.strip).values[0]

        # if there were no results, it's possible that first and last name in the metadata file were swapped.
        else:
            sql = sql_template.format(last, first)
            data = pd.read_sql(con=self._aims_con, sql=sql)

            data = data[
                (data['state_cd'] == state) & (data['lic_nbr'].apply(lambda x: str(lic_nbr) in x))].drop_duplicates()

            if len(data) == 1:
                return data['key_type_val'].apply(str.strip).values[0]

            # no results found either way
            else:
                return None

    def run(self):
        self._set_environment_variables()
        self._set_database_connections()
        uris = self._marklogic_con.get_file_uris()
        self._scan_uris(uris=uris)
