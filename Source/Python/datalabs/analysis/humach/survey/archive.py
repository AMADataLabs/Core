from dataclasses import dataclass
from datetime import datetime
import logging
import os
from sqlite3 import Connection

from dateutil.relativedelta import relativedelta
import pandas as pd

from datalabs.analysis.humach.survey.column_definitions import *
import settings


logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


@dataclass
class ExpectedFileColumns:
    standard_results = STANDARD_RESULTS_COLUMNS_EXPECTED
    validation_results = VALIDATION_RESULTS_COLUMNS_EXPECTED
    samples = SAMPLE_COLUMNS_EXPECTED
    dict = {
        'results_standard': standard_results,
        'results_validation': validation_results,
        'samples': samples
    }


@dataclass
class TableColumns:
    standard_results = STANDARD_RESULTS_COLUMNS
    validation_results = VALIDATION_RESULTS_COLUMNS
    samples = SAMPLE_COLUMNS
    dict = {
            'results_standard': standard_results,
            'results_validation': validation_results,
            'samples': samples
    }


class HumachResultsArchive:
    def __init__(self, database_path=None):
        self._database_path = database_path
        self.connection = None
        if self._database_path is not None:
            self.connection = Connection(self._database_path)

        # column names of tables in database
        self.table_columns = TableColumns()

        # column names of Excel files of samples sent to and results received from Humach
        self.expected_file_columns = ExpectedFileColumns()

        self._comment_end_dt_map = {
            'COMPLETE': False,
            'MOVED, NO FORWARDING INFO': True,
            'RETIRED': True,
            'WRONG NUMBER': True,
            'FAX MODEM': True,
            'DECEASED': True,
            'LANGUAGE/HEARING': False,
            'RESPONDED TO SURVEY - AMA': False,
            'REFUSAL': False,
            '2ND ATTEMPT': False,
            'NOT IN SERVICE': True,
            'ANSWERING SERVICE': False,
            'DO NOT CALL': True,
            'DUPLICATE': False,
            'FAIL': False
        }
        self._batch_load_save_dir = None

    def insert_row(self, table, vals):
        cols = self.table_columns.dict[table]

        sql = "INSERT INTO {}({}) VALUES({});".format(
                table,
                ','.join(cols),
                ','.join(['"' + str(v) + '"' for v in vals])
        )

        self.connection.execute(sql)

    def validate_cols(self, table, cols):
        cols_set = set(cols)
        expected_set = set(self.expected_file_columns.dict[table])
        if cols_set != expected_set:
            raise ValueError('Columns provided do not match columns expected.')

    def ingest_result_file(self, table, file_path):
        if table == 'results_standard':
            data = self._preprocess_standard_result_file(file_path)
        elif table == 'results_validation':
            data = self._preprocess_validation_result_file(file_path)
        else:
            raise ValueError('Table {} could not be processed.'.format(table))

        for i, r in data.iterrows():
            self.insert_row(table=table, vals=[v for v in r.values])

        self.connection.commit()

    def ingest_sample_file(self, file_path: str):
        data = pd.read_excel(file_path, dtype=str)
        self.ingest_sample_data(data=data)

    def ingest_sample_data(self, data: pd.DataFrame):
        df_cols = data.columns.values
        self.validate_cols(table='samples', cols=df_cols)
        data.fillna('', inplace=True)

        for i, r in data.iterrows():
            self.insert_row(table='samples', vals=[v for v in r.values])
        self.connection.commit()

    def get_sample_data(self, sample_ids: [str]) -> pd.DataFrame:
        table = 'samples'
        data = self.get_table_data_for_sample_ids(table=table, sample_ids=sample_ids)
        return data

    def get_sample_data_past_n_months(self, n, as_of_date: datetime.date = datetime.now().date()):
        sql = """SELECT * FROM samples"""
        data = pd.read_sql(sql=sql, con=self.connection)

        data['survey_date'] = [f'{year}-{("0" + str(month))[-2:]}-01' for year, month in zip(
            data['survey_year'].values,
            data['survey_month'].values)]
        data['survey_date'] = pd.to_datetime(data['survey_date'])
        data['survey_date'] = data['survey_date'].apply(lambda x: x.date())

        data['month_diff'] = [relativedelta(as_of_date, survey_date) for survey_date in data['survey_date'].values]
        data['month_diff'] = data['month_diff'].apply(lambda x: x.months)

        data = data[data['month_diff'] <= int(n)]

        del data['month_diff']

        return data

    def get_latest_sample_id(self):
        sql = """SELECT MAX(sample_id) FROM samples;"""
        result = self.connection.execute(sql).fetchone()[0]
        return result

    def get_latest_standard_sample_id(self):
        sql = "SELECT MAX(sample_id) FROM samples WHERE survey_type = 'STANDARD';"
        result = self.connection.execute(sql).fetchone()[0]
        return result

    def get_latest_survey_results_sample_id(self, survey_type):
        sql = \
            """
            SELECT MAX(r.sample_id) 
            FROM samples s 
            INNER JOIN results_{} r 
            ON (s.sample_id = r.sample_id AND s.row_id = r.row_id)
            WHERE s.survey_type = 'STANDARD';
            """.strip().format(survey_type)
        result = self.connection.execute(sql).fetchone()[0]
        return result

    def make_standard_batch_load_for_latest_result_sample_id(self):
        self._load_environment_variables()
        sample_id = self.get_latest_survey_results_sample_id(survey_type='standard')
        self.make_standard_batch_load([sample_id])

    def make_standard_batch_load(self, sample_ids: [str]):
        self._load_environment_variables()
        data = self.get_merged_survey_data(sample_type='standard', sample_ids=sample_ids)
        data['needs_end_date'] = [
            self._phone_needs_end_dt(
                given=g,
                received=r,
                comment=c
            ) for g, r, c in
            zip(
                data['sample_telephone_number'].values,
                data['result_office_telephone'].values,
                data['result_comments'].values
            )
        ]
        data_to_end_date = data[data['needs_end_date']]  # filter to needs_end_date == True
        data_to_end_date = self._prepare_batch_load_data(data=data_to_end_date)

        self._save_standard_batch_load_file(data_to_end_date)

    def get_merged_survey_data(self, sample_type: str, sample_ids: [str]) -> pd.DataFrame:
        sample_data = self.get_sample_data(sample_ids=sample_ids)
        result_data = self.get_result_data(sample_type=sample_type, sample_ids=sample_ids)

        # we need to rename table columns to avoid name overlap, except on match_cols
        match_cols = ['sample_id', 'row_id']
        sample_data.columns = self._add_column_prefixes(
            columns=sample_data.columns.values,
            prefix='sample',
            exclude_list=match_cols,
            exclude_prefixes=['sample', 'survey', 'row']
        )
        result_data.columns = self._add_column_prefixes(
            columns=result_data.columns.values,
            prefix='result',
            exclude_list=match_cols,
            exclude_prefixes=['sample', 'survey', 'row']
        )

        data = sample_data.merge(result_data, on=match_cols, how='inner')
        return data

    def get_result_data(self, sample_type: str, sample_ids: [str]) -> pd.DataFrame:
        data = self.get_table_data_for_sample_ids(table=f'results_{sample_type}', sample_ids=sample_ids)
        return data

    def get_table_data_for_sample_ids(self, table: str, sample_ids: [str]) -> pd.DataFrame:
        sql = \
            """
            SELECT *
            FROM {}
            WHERE {}.sample_id IN({})
            """.strip()
        sql = ' '.join([line.strip() for line in sql.splitlines()]).strip()
        sql = sql.format(
            table,
            table,
            ','.join(['"{}"'.format(str(sample_id)) for sample_id in sample_ids])
        )
        data = pd.read_sql(sql=sql, con=self.connection)
        return data

    def insert_humach_sample_reference(self, humach_sample_id, other_sample_id, other_sample_source):
        sql = f"INSERT INTO sample_reference(humach_sample_id, other_sample_id, other_sample_source) " + \
              f"VALUES ({humach_sample_id}, {other_sample_id}, '{other_sample_source}')"
        self.connection.execute(sql)
        self.connection.commit()

    def _load_environment_variables(self):
        self._batch_load_save_dir = os.environ.get('BATCH_LOAD_SAVE_DIR')
        if self.connection is None:
            self.connection = Connection(os.environ.get('ARCHIVE_DB_PATH'))

    def _preprocess_standard_result_file(self, filename: str) -> pd.DataFrame:
        data = pd.read_excel(filename, dtye=str)
        cols = data.columns.values
        self.validate_cols(table='results_standard', cols=cols)
        return data

    def _preprocess_validation_result_file(self, filename: str) -> pd.DataFrame:
        data = pd.DataFrame(columns=self.expected_file_columns.validation_results)
        sheet_names = ['ValidatedCorrect', 'ValidatedIncorrect', 'NotValidated', 'Unfinalized']
        for sheet_name in sheet_names:
            sheet_df = pd.read_excel(filename, sheet_name=sheet_name)
            data = data.append(sheet_df, ignore_index=True)
        return data

    def _phone_needs_end_dt(self, given: str, received: str, comment: str) -> bool:
        needs_end_dt = False
        comment_requires_end_dt = self._comment_end_dt_map[comment] if comment in self._comment_end_dt_map else False
        if given != received or comment_requires_end_dt:
            needs_end_dt = True

        return needs_end_dt

    @classmethod
    def _add_column_prefixes(cls, columns: [str], prefix: str, exclude_list=None, exclude_prefixes: [str] = None):
        """ Adds prefix to col names, unless the value is in the exclude list OR if value starts with exclude_prefix """
        if exclude_list is None:
            exclude_list = []
        if exclude_prefixes is None:
            exclude_prefixes = []
        renamed = []
        for col in columns:
            if col not in exclude_list or not any([col.startswith(prefix) for prefix in exclude_prefixes]):
                col = f'{prefix}_{col}'
            renamed.append(col)
        return renamed

    @classmethod
    def _prepare_batch_load_data(cls, data: pd.DataFrame) -> pd.DataFrame:
        data = data[['sample_me', 'sample_telephone_number']].rename(columns={
            'sample_me': 'me',
            'sample_telephone_number': 'phone'}
        ).drop_duplicates()
        # adds empty columns required by IT's process, even though they are un-used
        data['fax'] = ''
        data['source'] = ''
        data['verified_date'] = ''

        data['load_type'] = 'D'

        return data

    def _save_standard_batch_load_file(self, data: pd.DataFrame):
        today_date = str(datetime.now().date())
        file_name = f'HSG_PHYS_DELETES_{today_date}_StdKnownBad.csv'
        save_path = self._batch_load_save_dir + '/' + file_name

        data.to_csv(save_path, index=False)
