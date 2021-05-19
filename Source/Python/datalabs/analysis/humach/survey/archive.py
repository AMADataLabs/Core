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
        'humach_result': standard_results,
        'validation_result': validation_results,
        'humach_sample': samples
    }


@dataclass
class TableColumns:
    standard_results = STANDARD_RESULTS_COLUMNS
    validation_results = VALIDATION_RESULTS_COLUMNS
    samples = SAMPLE_COLUMNS
    dict = {
            'humach_result': standard_results,
            'validation_result': validation_results,
            'humach_sample': samples
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
                ','.join(['"' + str(v).replace(',', '').replace('"', '') + '"' for v in vals])
        )
        self.connection.execute(sql)


    def validate_cols(self, table, data, ignore_missing=False):
        """
        cols_set = sorted(set(cols))
        expected_set = sorted(set(self.expected_file_columns.dict[table]))
        if cols_set != expected_set:
            print(sorted(cols_set))
            print(sorted(expected_set))
            raise ValueError('Columns provided do not match columns expected.')
        """
        cols = data.columns.values
        for col in ['SAMPLE_ID', 'ROW_ID']:
            assert col in cols  # these columns must exist and not be null.
            assert not data[col].isna().any(), data[col].isna().any()

        if 'sample' in table:
            for col in ['SURVEY_MONTH', 'SURVEY_YEAR']:
                assert col in cols  # these columns are required for sample data

        for col in self.expected_file_columns.dict[table]:
            if 'VERIFIED/UPDATED' not in col:
                if ignore_missing and col not in cols:
                    data[col] = None
                else:
                    assert col in cols, col
        if 'SOURCE' in cols:
            del data['SOURCE']  # leftover column for ingesting sample files that were created with a different process
        return data

    def ingest_result_file(self, table, file_path):
        if table == 'humach_result':
            data = self._preprocess_standard_result_file(file_path)

            for i, r in data.iterrows():
                self.insert_row(table='humach_result', vals=[v for v in r.values])

        elif table == 'validation_result':
            data = self._preprocess_validation_result_file(file_path)

            for i, r in data.iterrows():
                self.insert_row(table='validation_result', vals=[v for v in r.values])

        else:
            raise ValueError(f'Table {table} could not be processed.')

        self.connection.commit()

    def ingest_result_data(self, data: pd.DataFrame):
        for i, r in data.iterrows():
            self.insert_row(table='humach_result', vals=[v for v in r.values])
        self.connection.commit()

    def ingest_sample_file(self, file_path: str, ignore_missing=False):
        data = pd.read_excel(file_path, dtype=str)
        self.ingest_sample_data(data=data, ignore_missing=ignore_missing)

    def ingest_sample_data(self, data: pd.DataFrame, ignore_missing=False):
        data = self.validate_cols(table='humach_sample', data=data, ignore_missing=ignore_missing)
        print('ingest sample data, cols:', data.columns.values)
        data.fillna('', inplace=True)
        print(data.head())

        for i, r in data.iterrows():
            try:
                self.insert_row(table='humach_sample', vals=[v for v in r.values])
            except:
                print('Probably too many values. Check columns in data:')
                print('Ingestion data columns:')
                print(data.columns.values)
                print(len(data.columns.values), 'columns found.')
                print('24 columns required. See table definition.')
                quit()
        self.connection.commit()

    def get_sample_data(self, sample_ids: [str]) -> pd.DataFrame:
        table = 'humach_sample'
        data = self.get_table_data_for_sample_ids(table=table, sample_ids=sample_ids)
        return data

    def get_sample_data_past_n_months(self, n, as_of_date: datetime.date = datetime.now().date()):
        sql = """SELECT * FROM humach_sample"""
        data = pd.read_sql(sql=sql, con=self.connection)

        data['survey_date'] = [f'{year}-{("0" + str(month))[-2:]}-01' for year, month in zip(
            data['survey_year'].values,
            data['survey_month'].values)]
        data['survey_date'] = pd.to_datetime(data['survey_date'], errors='coerce')
        data['survey_date'] = data['survey_date'].apply(lambda x: x.date())

        data['month_diff'] = [relativedelta(as_of_date, survey_date) for survey_date in data['survey_date'].values]
        data['month_diff'] = data['month_diff'].apply(lambda x: x.months)

        data = data[data['month_diff'] <= int(n)]

        del data['month_diff']

        return data

    def get_latest_sample_id(self):
        sql = """SELECT MAX(sample_id) FROM humach_sample;"""
        result = self.connection.execute(sql).fetchone()[0]
        return result

    def get_latest_standard_sample_id(self):
        sql = "SELECT MAX(sample_id) FROM humach_sample WHERE survey_type = 'STANDARD';"
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

    def make_standard_batch_load_for_results_in_survey_month_year(self, month, year):
        self._load_environment_variables()
        sql = \
            f"""
            SELECT DISTINCT(r.sample_id) FROM humach_result r
            INNER JOIN humach_sample s ON (r.sample_id = s.sample_id AND r.row_id = s.row_id) 
            WHERE s.survey_month = {month} AND s.survey_year = {year}
            """
        sample_ids = [sample_id[0] for sample_id in self.connection.execute(sql).fetchall()]
        LOGGER.info(f'Creating batch load for SAMPLE IDs: {sample_ids}')
        self.make_standard_batch_load(sample_ids=sample_ids)

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
        if sample_type == 'standard':
            table_name = 'humach_result'
        elif sample_type == 'validation':
            table_name = 'validation_result'
        else:
            raise ValueError('table_name not supported for sample_type:', sample_type)
        data = self.get_table_data_for_sample_ids(table=table_name, sample_ids=sample_ids)
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

        if 'SPECIALTY' not in data.columns.values:
            data['SPECIALTY'] = 0
            data['SPECIALTY UPDATED'] = 0
            data['PRESENT EMPLOYMENT UPDATED'] = 0
            data['COMMENTS'] = 'FAIL'

        formatted_data = pd.DataFrame()
        for col in data.columns.values:
            if 'VERIFIED UPDATED' in col:
                data[col.replace('VERIFIED UPDATED', 'VERIFIED/UPDATED')] = data[col]
                del data[col]

        for col in self.expected_file_columns.standard_results:
            #if 'VERIFIED/UPDATED' in col and 'VERIFIED/UPDATED' not in data.columns.values:
            #    data[col] = data[col.replace('VERIFIED/UPDATED', 'VERIFIED UPDATED')]
            #    print(col)
            formatted_data[col] = data[col]

        self.validate_cols(table='humach_result', data=data)
        formatted_data = formatted_data[formatted_data['SAMPLE_ID'].isna() == False]
        return formatted_data

    def _preprocess_validation_result_file(self, filename: str) -> pd.DataFrame:
        sheet_names = ['ValidatedCorrect', 'ValidatedIncorrect', 'NotValidated', 'Unfinalized']
        sheet_dataframes = []
        for sheet_name in sheet_names:
            sheet_df = pd.read_excel(filename, sheet_name=sheet_name)
            formatted_sheet_df = pd.DataFrame()
            for col in self.expected_file_columns.validation_results:
                formatted_sheet_df[col] = sheet_df[col]

            sheet_dataframes.append(sheet_df)

        formatted_data = pd.concat(sheet_dataframes)
        formatted_data = self.validate_cols(table='validation_result', data=formatted_data)
        return formatted_data

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
        if self._batch_load_save_dir is not None:
            save_path = self._batch_load_save_dir + '/' + file_name
        else:
            save_path = file_name
        data.to_csv(save_path, index=False)
