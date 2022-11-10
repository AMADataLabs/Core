""" Old code for PoC project to identify metadata files without ME number filled """
# pylint: disable=no-name-in-module,import-error,wildcard-import,undefined-variable,protected-access,unused-import,too-many-instance-attributes,logging-fstring-interpolation,unnecessary-lambda,abstract-class-instantiated,logging-format-interpolation,no-member,trailing-newlines,trailing-whitespace,function-redefined,use-a-generator
import json
import os

import pandas as pd

from   datalabs.access import jdbc
from   datalabs.access import odbc
from   datalabs.access.sanctions.marklogic import MarkLogic
from  datalabs.analysis.sanctions.me.sql import SQL_TEMPLATE


class SanctionsMEScan:
    def __init__(self):
        self._marklogic = None
        self._aims = None
        self._aims_source_name = None
        self._aims_username = None
        self._aims_password = None

    def run(self):
        self._load_environment_variables()

        self._marklogic, self._aims = self._setup_database_connections()

        uris = self._marklogic.get_file_uris()

        self._scan_uris(uris)

    def _load_environment_variables(self):
        self._aims_source_name = os.environ.get('DATABASE_NAME_AIMS')
        self._aims_username = os.environ.get('CREDENTIALS_AIMS_USERNAME')
        self._aims_password = os.environ.get('CREDENTIALS_AIMS_PASSWORD')

    def _setup_database_connections(self, use_jdbc=True):
        with MarkLogic.from_environment('MARKLOGIC_PROD') as marklogic:
            aims = None

            if use_jdbc:
                aims = self._setup_jdbc_aims_connection()
            else:
                aims = self._setup_odbc_aims_connection()

            yield marklogic, aims

    def _scan_uris(self, uris: list):
        """
        Scans MarkLogic for metadata files specified by a list of uris. If the metadata file is eligible for
        an ME lookup
        :param uris: list of MarkLogic document URIs--sanction metadata files--to scan
        :return: None
        """
        uris = [f for f in uris if 'summarylist' not in f]  # remove Summary List files
        for uri in uris:
            self._scan_uri(uri)

    def _setup_jdbc_aims_connection(self):
        database_parameters = dict(
            driver='com/informix/jdbc/IfxConnection',
            driver_type='informix-sqli',
            host='rdbp1627.ama-assn.org',
            username=self._aims_username,
            password=self._aims_password,
            port='22093',
            jar_path='./jdbc-4.50.2.fix-1.jar',
            name='aims_prod:informixserver=prd1srvxnet'
        )

        with jdbc.Database(database_parameters) as aims:
            aims.connection.cursor().execute('SET ISOLATION TO DIRTY READ;')

            yield aims

    def _setup_odbc_aims_connection(self):
        database_parameters = dict(
            name="aims_prod",
            username=self._aims_username,
            password=self._aims_password
        )

        with odbc.Database(database_parameters) as aims:
            yield aims

    @classmethod
    def _get_state(cls, uri: str):
        # example - '/json/2019.10.30_OH_NA_SL/schwartz_2172.json'
        _sl_index = uri.index('_SL/')
        return uri[_sl_index - 5:_sl_index - 3]

    def _scan_uri(self, uri: str):
        # get the json file for this URI
        json_data = json.loads(self._marklogic.get_file(uri=uri))

        if self._needs_me(json_data) and self._is_searchable(json_data):
            first = json_data['sanction']['physician']['name_first']
            last = json_data['sanction']['physician']['name_last']
            state = self._get_state(uri)

            me_number = self._get_me_number(first=first, last=last, state=state)
            if me_number is not None:
                self._marklogic.set_me_number(uri=uri, json_file=json_data, me_number=me_number)

    @classmethod
    def _is_null(cls, value):
        return value in ['None', None, 'Null', 'none', 'null', 'NA', 'na', '']

    @classmethod
    def _needs_me(cls, json_data):
        try:
            me_number = json_data['sanction']['physician']['me']
            return cls._is_null(me_number)
        except KeyError:  # json_data not formatted properly
            return False

    def _is_searchable(self, json_data):
        first = json_data['sanction']['physician']['name_first']
        last = json_data['sanction']['physician']['name_last']
        # if any of these are null, we can't search for ME number. NOT any null = ALL non-null = searchable
        return not any([self._is_null(val) for val in [first, last]])

    def _get_me_number(self, first, last, state):
        """
        Initial search is just on first + last because I was getting some weird errors / unexpected behavior when
        using state_cd to compare to state in the SQL query. Final matching on state is done
        once the initial results are in a DataFrame.
        """

        sql = SQL_TEMPLATE.format(first.upper(), last.upper())
        sql_reversed = SQL_TEMPLATE.format(last.upper(), first.upper())

        data = self._aims.read(sql)

        data = data[data['state_cd'] == state].drop_duplicates()

        me_number = None
        if len(data) == 1:  # no dupes
            me_number = data['key_type_val'].apply(str.strip).values[0]

        else:  # try with swapped first/last name
            data = self._aims.read(sql_reversed)
            data = data[data['state_cd'] == state].drop_duplicates()
            if len(data) == 1:  # no dupes
                me_number = data['key_type_val'].apply(str.strip).values[0]

        return me_number
