from sqlite3 import Connection
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta


class HumachResultsArchive:
    def __init__(self, database):
        self.connection = Connection(database)

        # column names of tables in database
        self.standard_results_cols = ['sample_id',
                                      'row_id',
                                      'physician_me_number',
                                      'physician_first_name',
                                      'physician_middle_name',
                                      'physician_last_name',
                                      'suffix',
                                      'degree',
                                      'office_address_line_1',
                                      'office_address_line_2',
                                      'office_address_city',
                                      'office_address_state',
                                      'office_address_zip',
                                      'office_address_verified_updated',
                                      'office_telephone',
                                      'office_phone_verified_updated',
                                      'office_fax',
                                      'office_fax_verified_updated',
                                      'specialty',
                                      'specialty_updated',
                                      'present_employment_code',
                                      'present_employment_updated',
                                      'comments',
                                      'source',
                                      'source_date']
        self.validation_results_cols = [
            'sample_id',
            'row_id',
            'study_cd',
            'me_no',
            'fname',
            'mname',
            'lname',
            'suffix',
            'degree',
            'lable_name',
            'office_phone',
            'polo_addr_line_0',
            'polo_addr_line_1',
            'polo_addr_line_2',
            'polo_city',
            'polo_state',
            'polo_zip',
            'polo_zipext',
            'original_phone',
            'correct_phone',
            'reason_phone_incorrect',
            'reason_phone_other',
            'captured_number',
            'correct_address',
            'reason_addr_incorrect',
            'reason_addr_other',
            'no_longer_at_addr_comment',
            'captured_add0',
            'captured_add1',
            'captured_add2',
            'captured_city',
            'captured_state',
            'captured_zip',
            'captured_zipext',
            'lastcall',
            'adcid',
            'secondattempt',
            'result_of_call']
        self.sample_cols = ['sample_id',
                            'row_id',
                            'survey_month',
                            'survey_year',
                            'survey_type',
                            'sample_source',
                            'me',
                            'entity_id',
                            'first_name',
                            'middle_name',
                            'last_name',
                            'suffix',
                            'polo_comm_id',
                            'polo_mailing_line_1',
                            'polo_mailing_line_2',
                            'polo_city',
                            'polo_state',
                            'polo_zip',
                            'phone_comm_id',
                            'telephone_number',
                            'prim_spec_cd',
                            'description',
                            'pe_cd',
                            'fax_number']

        # column names of Excel files sent/received to/from Humach
        self.standard_results_cols_expected = ['SAMPLE_ID',
                                               'ROW_ID',
                                               'PHYSICIAN ME NUMBER',
                                               'PHYSICIAN FIRST NAME',
                                               'PHYSICIAN MIDDLE NAME',
                                               'PHYSICIAN LAST NAME',
                                               'SUFFIX',
                                               'DEGREE',
                                               'OFFICE ADDRESS LINE 1',
                                               'OFFICE ADDRESS LINE 2',
                                               'OFFICE ADDRESS CITY',
                                               'OFFICE ADDRESS STATE',
                                               'OFFICE ADDRESS ZIP',
                                               'OFFICE ADDRESS VERIFIED/UPDATED',
                                               'OFFICE TELEPHONE',
                                               'OFFICE PHONE VERIFIED/UPDATED',
                                               'OFFICE FAX',
                                               'OFFICE FAX VERIFIED/UPDATED',
                                               'SPECIALTY',
                                               'SPECIALTY UPDATED',
                                               'PRESENT EMPLOYMENT CODE',
                                               'PRESENT EMPLOYMENT UPDATED',
                                               'COMMENTS',
                                               'SOURCE',
                                               'SOURCE DATE']
        self.validation_results_cols_expected = ['SAMPLE_ID',
                                                 'ROW_ID',
                                                 'STUDY_CD',
                                                 'ME_NO',
                                                 'FNAME',
                                                 'MNAME',
                                                 'LNAME',
                                                 'SUFFIX',
                                                 'DEGREE',
                                                 'LABLE_NAME',
                                                 'OFFICE_PHONE',
                                                 'POLO_ADDR_LINE_0',
                                                 'POLO_ADDR_LINE_1',
                                                 'POLO_ADDR_LINE_2',
                                                 'POLO_CITY',
                                                 'POLO_STATE',
                                                 'POLO_ZIP',
                                                 'POLO_ZIPEXT',
                                                 'ORIGINAL_PHONE',
                                                 'CORRECT_PHONE',
                                                 'REASON_PHONE_INCORRECT',
                                                 'REASON_PHONE_OTHER',
                                                 'CAPTURED_NUMBER',
                                                 'CORRECT_ADDRESS',
                                                 'REASON_ADDR_INCORRECT',
                                                 'REASON_ADDR_OTHER',
                                                 'NO_LONGER_AT_ADDR_COMMENT',
                                                 'CAPTURED_ADD0',
                                                 'CAPTURED_ADD1',
                                                 'CAPTURED_ADD2',
                                                 'CAPTURED_CITY',
                                                 'CAPTURED_STATE',
                                                 'CAPTURED_ZIP',
                                                 'CAPTURED_ZIPEXT',
                                                 'LASTCALL',
                                                 'ADCID',
                                                 'SECONDATTEMPT',
                                                 'RESULT_OF_CALL']
        self.sample_cols_expected = ['SAMPLE_ID',
                                     'ROW_ID',
                                     'SURVEY_MONTH',
                                     'SURVEY_YEAR',
                                     'SURVEY_TYPE',
                                     'SAMPLE_SOURCE',
                                     'ME',
                                     'ENTITY_ID',
                                     'FIRST_NAME',
                                     'MIDDLE_NAME',
                                     'LAST_NAME',
                                     'SUFFIX',
                                     'POLO_COMM_ID',
                                     'POLO_MAILING_LINE_1',
                                     'POLO_MAILING_LINE_2',
                                     'POLO_CITY',
                                     'POLO_STATE',
                                     'POLO_ZIP',
                                     'PHONE_COMM_ID',
                                     'TELEPHONE_NUMBER',
                                     'PRIM_SPEC_CD',
                                     'DESCRIPTION',
                                     'PE_CD',
                                     'FAX_NUMBER']

    def insert_row(self, table, vals):
        if table == 'results_standard':
            cols = self.standard_results_cols
        elif table == 'results_validation':
            cols = self.validation_results_cols
        elif table == 'samples':
            cols = self.sample_cols
        else:
            raise ValueError('Table must be "results_standard", "results_validation", or "samples"')

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
        assert table in ['results_standard', 'results_validation']

        if table == 'results_standard':
            df = pd.read_excel(file_path, dtype=str)
            df_cols = df.columns.values
            self.validate_cols(table=table, cols=df_cols)
        else:
            df = pd.DataFrame(columns=self.validation_results_cols_expected)
            sheet_names = ['ValidatedCorrect', 'ValidatedIncorrect', 'NotValidated', 'Unfinalized']
            for sheet_name in sheet_names:
                print('Extracting data from sheet: {}'.format(sheet_name))
                sheet_df = pd.read_excel(file_path, sheet_name=sheet_name)
                df = df.append(sheet_df, ignore_index=True)

        for i, r in df.iterrows():
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



