from sqlite3 import Connection
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta

from datalabs.analysis.humach.survey.column_definitions import *


class HumachResultsArchive:
    def __init__(self, database):
        self.connection = Connection(database)

        # column names of tables in database
        self.standard_results_cols = STANDARD_RESULTS_COLUMNS
        self.validation_results_cols = VALIDATION_RESULTS_COLUMNS
        self.sample_cols = SAMPLE_COLUMNS

        # column names of Excel files sent/received to/from Humach
        self.standard_results_cols_expected = STANDARD_RESULTS_COLUMNS_EXPECTED
        self.validation_results_cols_expected = VALIDATION_RESULTS_COLUMNS_EXPECTED
        self.sample_cols_expected = SAMPLE_COLUMNS_EXPECTED

        self.table_columns = {
            'results_standard': self.standard_results_cols,
            'results_validation': self.validation_results_cols,
            'samples': self.sample_cols
        }

    def insert_row(self, table, vals):
        cols = self.table_columns[table]

        sql = \
            "INSERT INTO {}({}) VALUES({});".format(table, ','.join(cols), ','.join(['"' + str(v) + '"' for v in vals]))

        self.connection.execute(sql)

    def validate_cols(self, table, cols):
        cols_set = set(cols)
        if table == 'results_standard':
            expected_set = set(self.standard_results_cols_expected)
        elif table == 'results_validation':
            expected_set = set(self.validation_results_cols_expected)
        elif table == 'samples':
            expected_set = set(self.sample_cols_expected)
        else:
            expected_set = None
        assert cols_set == expected_set, f'{cols_set}' + f'\n{expected_set}'

    def ingest_result_file(self, table, file_path):
        if table == 'results_standard':
            data = self._preprocess_standard_result_file(file_path)
        elif table == 'results_validation':
            data = self._preprocess_validation_result_file(file_path)
        else:
            raise

        for i, r in data.iterrows():
            self.insert_row(table=table, vals=[v for v in r.values])

        self.connection.commit()

    def _preprocess_standard_result_file(self, filename: str) -> pd.DataFrame:
        data = pd.read_excel(filename, dtye=str)
        cols = data.columns.values
        self.validate_cols(table='results_standard', cols=cols)
        return data

    def _preprocess_validation_result_file(self, filename: str) -> pd.DataFrame:
        data = pd.DataFrame(columns=self.validation_results_cols_expected)
        sheet_names = ['ValidatedCorrect', 'ValidatedIncorrect', 'NotValidated', 'Unfinalized']
        for sheet_name in sheet_names:
            # print('Extracting data from sheet: {}'.format(sheet_name))
            sheet_df = pd.read_excel(filename, sheet_name=sheet_name)
            data = data.append(sheet_df, ignore_index=True)
        return data

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

    def get_sample_data(self, sample_ids: [str]):
        sql = \
            """
            SELECT *
            FROM samples
            WHERE samples.sample_id IN({})
            """.strip()
        sql = ' '.join([line.strip() for line in sql.splitlines()]).strip()
        sql = sql.format(','.join(['"{}"'.format(str(sample_id)) for sample_id in sample_ids]))
        print(sql)
        data = pd.read_sql(sql=sql, con=self.connection)
        return data

    def get_sample_data_past_n_months(self, n, as_of_date: datetime.date = datetime.now().date()):
        sql = \
            """SELECT * FROM samples"""
        data = pd.read_sql(sql=sql, con=self.connection)

        data['survey_date'] = [f'{year}-{("0" + str(month))[-2:]}-01' for year,
                                                                          month in zip(data['survey_year'].values,
                                                                                       data['survey_month'].values)]
        data['survey_date'] = pd.to_datetime(data['survey_date'])
        data['survey_date'] = data['survey_date'].apply(lambda x: x.date())

        data['month_diff'] = [relativedelta(as_of_date, survey_date) for survey_date in data['survey_date'].values]
        data['month_diff'] = data['month_diff'].apply(lambda x: x.months)

        data = data[data['month_diff'] <= int(n)]

        del data['month_diff']

        return data

    def get_latest_sample_id(self):
        sql = \
            """SELECT MAX(sample_id) FROM samples;"""
        result = self.connection.execute(sql).fetchone()[0]
        return result



