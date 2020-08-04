import json
import os
import pandas as pd
import jaydebeapi
from datalabs.access.sanctions.marklogic import MarkLogic
from datalabs.analysis.sanctions.me.sql import SQL_TEMPLATE
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
        self._marklogic_con = MarkLogic(server='prod')

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
            self._scan_uri(uri)

    def _scan_uri(self, uri: str):
        # download the json file for this URI
        json_data = json.loads(self._marklogic_con.get_file(uri=uri))

        if self._needs_me(json_data) and self._is_searchable(json_data):
            lic_nbr = json_data['sanction']['physician']['license']
            first = json_data['sanction']['physician']['name_first']
            last = json_data['sanction']['physician']['name_last']
            state = self._get_state(uri)

            me_nbr = self._get_me_nbr(first=first,
                                      last=last,
                                      state=state,
                                      lic_nbr=lic_nbr)
            if me_nbr is not None:
                self._marklogic_con.set_me_nbr(uri=uri,
                                               json_file=json_data,
                                               me_nbr=me_nbr)

    @classmethod
    def _is_null(cls, value):
        return value in ['None', None, 'Null', 'none', 'null', 'NA', 'na', '']

    @classmethod
    def _needs_me(cls, json_data):
        try:
            me_nbr = json_data['sanction']['physician']['me']
            return cls._is_null(me_nbr)
        except:  # json_data not formatted properly
            return False

    def _is_searchable(self, json_data):
        lic_nbr = json_data['sanction']['physician']['license']
        first = json_data['sanction']['physician']['name_first']
        last = json_data['sanction']['physician']['name_last']
        # if any of these are null, we can't search for ME nbr. NOT any null = ALL non-null = searchable
        return not any([self._is_null(val) for val in [lic_nbr, first, last]])

    def _get_me_nbr(self, first, last, state, lic_nbr):
        """
        initial search is just on first + last because I was getting some weird errors / unexpected behavior when
        using state_cd to compare to state in the SQL query. Final matching on state and license number are done
        once the initial results are in a DataFrame.
        """

        sql = SQL_TEMPLATE.format(first.upper(), last.upper())
        sql_reversed = SQL_TEMPLATE.format(last.upper(), first.upper())

        data = pd.read_sql(con=self._aims_con, sql=sql)

        data = data[
            (data['state_cd'] == state) & (data['lic_nbr'].apply(lambda x: str(lic_nbr) in x))].drop_duplicates()

        me_nbr = None
        if len(data) == 1:  # no dupes
            me_nbr = data['key_type_val'].apply(str.strip).values[0]

        else:  # try with swapped first/last name
            data = pd.read_sql(con=self._aims_con, sql=sql_reversed)
            data = data[
                (data['state_cd'] == state) & (data['lic_nbr'].apply(lambda x: str(lic_nbr) in x))].drop_duplicates()
            if len(data) == 1:  # no dupes
                me_nbr = data['key_type_val'].apply(str.strip).values[0]

        return me_nbr

    def run(self):
        self._set_environment_variables()
        self._set_database_connections()
        uris = self._marklogic_con.get_file_uris()
        self._scan_uris(uris=uris)
