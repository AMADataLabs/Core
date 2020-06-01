from sqlite3 import Connection
import pandas as pd

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

        # column names of Excel files from Humach
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
        self.validation_results_cols_expected = []

    # vals - a list of values corresponding to standard_results_cols
    def insert_row(self, table, vals):
        if table == 'results_standard':
            cols = self.standard_results_cols
        elif table == 'results_validation':
            cols = self.validation_results_cols
        else:
            raise ValueError('Table must be results_standard or results_validation')

        sql = \
            "INSERT INTO {}({}) VALUES({});".format(table, ','.join(cols), ','.join(['"' + str(v) + '"' for v in vals]))

        print(sql)
        self.connection.execute(sql)

    def validate_cols(self, table, cols):
        cols_set = set(cols)
        if table == 'results_standard':
            expected_set = set(self.standard_results_cols_expected)
        elif table == 'results_validation':
            expected_set = set(self.validation_results_cols_expected)
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
