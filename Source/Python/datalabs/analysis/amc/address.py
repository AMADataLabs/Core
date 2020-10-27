from datetime import datetime
import numpy as np
import os
import pandas as pd
import string

import logging
logging.basicConfig(level=logging.INFO)

from datalabs.access.aims import AIMS
from datalabs.access import excel
from datalabs.messaging.outlook import Outlook


class AMCAddressFlagger:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

        self._today_date = str(datetime.now().date())

        self._output_file = None

        self._amc_query_file = None
        self._flag_word_file = None

        self._output_directory = None
        self._output_file_password = None

        self._report_sender = None
        self._report_recipients = None
        self._report_cc = None

        self._false_positives = None

    def _get_flag_words(self):
        flag_words = pd.read_excel(self._flag_word_file, header=None)[0].values
        flag_words = [str(word).lower() for word in flag_words]

        return flag_words

    def _get_amc_address_data(self):
        with open(self._amc_query_file, 'r') as f:
            sql = f.read()
        with AIMS() as aims:
            data = aims.read(sql=sql, coerce_float=False)

        return self._clean_str_data(data)

    @classmethod
    def _is_flagged_city(cls, city_string):
        city_string = city_string.lower()
        return any([city_string == '',
                    not cls._contains_n_unique_chars(city_string, 2),
                    cls._contains_any_digits(city_string)])

    @classmethod
    def _is_flagged_addr1(cls, addr1_string, flag_null=False):
        flag = False

        if not flag_null:
            if addr1_string is not None and len(addr1_string) != 0:
                addr1_string = addr1_string.lower()
                if not cls._contains_n_unique_chars(addr1_string, 2):
                    flag = True

        if flag_null:
            if addr1_string is None or len(addr1_string) == 0 or addr1_string == '':
                flag = True
        return flag

    @classmethod
    def _is_flagged_addr2(cls, addr2_string):
        flag = False

        if addr2_string is None or len(addr2_string) == 0:
            flag = True

        elif not cls._contains_n_unique_chars(addr2_string, 2) or addr2_string.isdigit():
            flag = True

        return flag

    @classmethod
    def _contains_n_unique_chars(cls, text, n):
        chars = set(text.lower())
        return len(chars) >= n

    @classmethod
    def _contains_only_ascii_chars(cls, text):
        only_ascii = True
        for char in text:
            if char not in string.ascii_letters:
                only_ascii = False
                break
        return only_ascii

    @classmethod
    def _contains_only_digits(cls, text):
        only_digits = True
        for char in text:
            if char not in string.digits:
                only_digits = False
                break
        return only_digits

    @classmethod
    def _contains_any_digits(cls, text):
        any_digits = False
        for char in text:
            if char in string.digits:
                any_digits = True
                break
        return any_digits

    @classmethod
    def _is_flagged_state(cls, state_string):
        return any([state_string is None,
                    len(state_string) != 2,
                    not cls._contains_n_unique_chars(state_string, 2),
                    not cls._contains_only_ascii_chars(state_string)])

    @classmethod
    def _is_flagged_zip(cls, zip_string):
        flag = False

        if zip_string is None:
            flag = True

        # if any non-digits or len > 5
        if any([not cls._contains_only_digits(zip_string),
                len(zip_string) > 5]):
            flag = True

        return flag

    def _contains_flagword(self, address_string, flag_words):
        """
        We want to avoid false positive markers from flagging the method that checks for flag words.
        this is done by removing the text of false positives from the aggregated address text before
        we search that text for flag words.
        """
        address_string = address_string.lower()
        for fp in self._false_positives:
            if fp in address_string:
                address_string = address_string.replace(fp, '')

        tokens = address_string.split()

        return any([t in flag_words for t in tokens])

    @classmethod
    def _clean_str_data(cls, data: pd.DataFrame):
        data.fillna('', inplace=True)
        data.replace(np.nan, '', inplace=True, regex=True)

        for col in data.columns.values:
            data[col] = data[col].astype(str).apply(lambda x: x.strip())

        data['address'] = data['addr_line0'].str.lower() + ' ' + \
                          data['addr_line1'].str.lower() + ' ' + \
                          data['addr_line2'].str.lower() + ' ' + \
                          data['city_cd'].str.lower() + ' ' + \
                          data['state_cd'].str.lower()
        data['usg_begin_dt'] = data['usg_begin_dt'].apply(lambda x: x.replace('[', '').replace(']', ''))
        data['usg_begin_dt'] = data['usg_begin_dt'].apply(lambda x: x[:x.index(':')] if ':' in x else x)
        data['usg_begin_dt'] = pd.to_datetime(data['usg_begin_dt'])

        return data

    def _get_flagged_data_and_summary(self, data):
        self.logger.info('\tAdding flag indicator columns:')
        self.logger.info('\t\taddr1')
        data['addr1_flagged'] = data['addr_line1'].apply(lambda x: self._is_flagged_addr1(x))
        self.logger.info('\t\taddr2')
        data['addr2_flagged'] = data['addr_line2'].apply(lambda x: self._is_flagged_addr2(x))
        self.logger.info('\t\tcity')
        data['city_flagged'] = data['city_cd'].apply(lambda x: self._is_flagged_city(x))
        self.logger.info('\t\tstate')
        data['state_flagged'] = data['state_cd'].apply(lambda x: self._is_flagged_state(x))
        self.logger.info('\t\tzip')
        data['zip_flagged'] = data['zip'].apply(lambda x: self._is_flagged_zip(x))

        flag_words = self._get_flag_words()
        self.logger.info('\t\tflagwords')
        data['contains_flag_word'] = data['address'].apply(lambda x: self._contains_flagword(x, flag_words))

        data.drop_duplicates(inplace=True)
        self.logger.info('\tGetting flag type counts.')

        # flag type ounts
        n_addr1     = len(data[data['addr1_flagged']])
        n_addr2     = len(data[data['addr2_flagged']])
        n_city      = len(data[data['city_flagged']])
        n_state     = len(data[data['state_flagged']])
        n_zip       = len(data[data['zip_flagged']])
        n_flagwords = len(data[data['contains_flag_word']])

        flags = {
            'addr_line1': n_addr1,
            'addr_line2': n_addr2,
            'city': n_city,
            'state': n_state,
            'zip': n_zip,
            'flag_word': n_flagwords}

        # compile records that have any flag
        self.logger.info('\tCompiling flagged Records.')
        any_flags = []
        for i, row in data.iterrows():
            a = any([row['addr1_flagged'],
                     row['addr2_flagged'],
                     row['city_flagged'],
                     row['state_flagged'],
                     row['zip_flagged'],
                     row['contains_flag_word']])
            any_flags.append(a)

        data['any_flag'] = any_flags
        results_summary = ''
        results_summary += f"<br>Count of all flagged amc-sourced addresses: {len(data[data['any_flag']])}"
        results_summary += '<br>Flagging summary: (addresses can be flagged by multiple fields, ' \
                           'so the sum of these counts may exceed count above)'
        for f in flags:
            count = flags[f]
            if count > 0:
                results_summary += f'<br>{"&nbsp"*13}  {f}: {count}'

        data.drop(columns='address', axis=1, inplace=True)  # delete temp column

        flagged_data = data[data['any_flag']]
        flagged_data['date_checked'] = self._today_date

        return flagged_data, results_summary

    def _save_output(self, data: pd.DataFrame):
        excel.save_formatted_output(data, self._output_file, 'AMC Address Sweep')
        excel.add_password_to_xlsx(self._output_file, self._output_file_password)

    def _get_env_variables(self):
        self._amc_query_file = os.environ.get('AMC_QUERY_FILE')
        self._flag_word_file = os.environ.get('FLAG_WORD_FILE')

        self._output_directory = os.environ.get('OUTPUT_DIRECTORY')
        self._output_file_password = os.environ.get('OUTPUT_FILE_PASSWORD')
        self._output_file = f'{self._output_directory}/AMC_flagged_addresses_{self._today_date}.xlsx'

        self._report_sender = os.environ.get('REPORT_SENDER')
        self._report_recipients = os.environ.get('REPORT_RECIPIENTS').split(',')
        self._report_cc = os.environ.get('REPORT_CC').split(',')

        self._false_positives = os.environ.get('FALSE_POSITIVES').split(',')

    def run(self):
        self.logger.info('Getting required environment variables.')
        self._get_env_variables()
        self.logger.info('Querying active amc-sourced address data.')
        data = self._get_amc_address_data()
        self.logger.info('Cleaning data.')
        data = self._clean_str_data(data).drop_duplicates()

        flagged_data, summary = self._get_flagged_data_and_summary(data)
        flagged_data.drop_duplicates(inplace=True)
        self.logger.info('Saving results.')
        self._save_output(flagged_data)

        self.logger.info('Creating email report.')
        report_body = \
            '<p>Hello!' + \
            '<br>Attached are the latest results of the AMC address flagging script.' + \
            '<br>Password: Survey20' + '</p>' + \
            '<p>Results summary:' + \
            summary + '</p>' + \
            '<p>This report and email were generated automatically.' + \
            '<br>If you believe there are errors or if you have questions or suggestions, please contact Garrett.</p>'

        outlook = Outlook()
        outlook.send_email(to=self._report_recipients,
                           cc=self._report_cc,
                           subject=f'AMC Sweep Results - {self._today_date}',
                           body=report_body,
                           from_account=self._report_sender,
                           attachments=[self._output_file],
                           auto_send=False)
