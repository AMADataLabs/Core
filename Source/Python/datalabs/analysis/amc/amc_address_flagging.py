from datetime import datetime
import numpy as np
import os
import pandas as pd
import string

import logging
logging.basicConfig(level=logging.INFO)

from datalabs.access.aims import AIMS
from datalabs.common import excel
from datalabs.messaging.outlook import Outlook

import settings


class AMCFlagger:
    def __init__(self):
        self.logger = logging.getLogger('info')

        self.TODAY_DATE = str(datetime.now().date())

        self.OUTPUT_FILE = None

        self.AMC_QUERY_FILE = None
        self.FLAG_WORD_FILE = None

        self.OUTPUT_DIRECTORY = None
        self.OUTPUT_FILE_PASSWORD = None

        self.REPORT_SENDER = None
        self.REPORT_RECIPIENTS = None
        self.REPORT_CC = None

        self.FALSE_POSITIVES = None

    def _get_flag_words(self):
        flag_words = pd.read_excel(self.FLAG_WORD_FILE, header=None)[0].values
        flag_words = [str(word).lower() for word in flag_words]

        return flag_words

    def _get_amc_address_data(self):
        with open(self.AMC_QUERY_FILE, 'r') as f:
            sql = f.read()
        with AIMS() as aims:
            data = aims.read(sql=sql, coerce_float=False)

        data = self._clean_str_data(data)
        return data

    @classmethod
    def _is_flagged_city(cls, city_string):
        city_string = city_string.lower()
        return any([city_string == '',
                    len(set(city_string)) == 1,
                    any([d in city_string for d in string.digits])])

    @classmethod
    def _is_flagged_addr1(cls, addr1_string, flag_null=False):
        flag = False

        if not flag_null:
            if addr1_string is not None and len(addr1_string) != 0:
                addr1_string = addr1_string.lower()
                # if address only contains 1 unique character
                if len(set(addr1_string)) <= 1:
                    flag = True

        if flag_null:
            if addr1_string is None or len(addr1_string) == 0 or addr1_string == '':
                flag = True
        return flag

    @classmethod
    def _is_flagged_addr2(cls, addr2_string):
        flag = False

        # if null or empty
        if addr2_string is None or len(addr2_string) == 0:
            flag = True

        # if addr2 is a digit or has <= 2 unique characters
        elif len(set(addr2_string)) <= 2 or addr2_string.isdigit():
            flag = True

        return flag

    @classmethod
    def _is_flagged_state(cls, state_string):
        # if null, not 2 characters, not 2 unique characters, any non-ascii letters
        return any([state_string is None,
                    all([len(state_string) != 2, any([not isinstance(c, str) for c in state_string])]),
                    len(set(state_string.lower())) != 2,
                    any([c not in string.ascii_letters for c in state_string])])

    @classmethod
    def _is_flagged_zip(cls, zip_string):
        flag = False

        if zip_string is None:
            flag = True

        # if any non-digits or len > 5
        if any([any([c not in string.digits for c in zip_string]),
                len(zip_string) > 5]):
            flag = True

        return flag

    def _contains_flagword(self, address_string, flag_words):
        address_string = address_string.lower()

        # we want to avoid false positive markers from flagging the method that checks for flag words.
        # this is done by removing the text of false positives from the aggregated address text before
        # we search that text for flag words.
        for fp in self.FALSE_POSITIVES:
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
        results_summary += f"Count of all flagged amc-sourced addresses:{len(data[data['any_flag']])}"
        results_summary += '\nFlagging summary: (addresses can be flagged by multiple fields, ' \
                           'so the sum of these could exceed count above)'
        for f in flags:
            val = flags[f]
            if val > 0:
                results_summary += '\n\t{}: {}'.format(f, val)

        data.drop(columns='address', axis=1, inplace=True)  # delete temp column

        flagged_data = data[data['any_flag']]
        flagged_data['date_checked'] = self.TODAY_DATE

        return flagged_data, results_summary

    def _save_output(self, data: pd.DataFrame):
        excel.save_formatted_output(data, self.OUTPUT_FILE, 'amc Address Sweep')
        excel.add_password_to_xlsx(self.OUTPUT_FILE, self.OUTPUT_FILE_PASSWORD)

    def _get_env_variables(self):
        self.AMC_QUERY_FILE = os.environ.get('AMC_QUERY_FILE')
        self.FLAG_WORD_FILE = os.environ.get('FLAG_WORD_FILE')

        self.OUTPUT_DIRECTORY = os.environ.get('OUTPUT_DIRECTORY')
        self.OUTPUT_FILE_PASSWORD = os.environ.get('OUTPUT_FILE_PASSWORD')
        self.OUTPUT_FILE = f'{self.OUTPUT_DIRECTORY}/AMC_flagged_addresses_{self.TODAY_DATE}.xlsx'

        self.REPORT_SENDER = os.environ.get('REPORT_SENDER')
        self.REPORT_RECIPIENTS = os.environ.get('REPORT_RECIPIENTS').split(',')
        self.REPORT_CC = os.environ.get('REPORT_CC').split(',')

        self.FALSE_POSITIVES = os.environ.get('FALSE_POSITIVES').split(',')

    def run(self):
        self.logger.info('Getting required environment variables.')
        self._get_env_variables()
        self.logger.info('Querying active amc-sourced address data.')
        data = self._get_amc_address_data()
        self.logger.info('Cleaning data.')
        data = self._clean_str_data(data)

        flagged_data, summary = self._get_flagged_data_and_summary(data)
        self.logger.info('Saving results.')
        self._save_output(flagged_data)

        self.logger.info('Creating email report.')
        report_body = \
        'Hello!\n\n' + \
        'Attached are the latest results of the amc address flagging script.\n\n' + \
        'Password: Survey20\n\n' + \
        'Results summary:\n' + \
        summary + \
        '\n\nThis report and email were generated automatically.\n' + \
        'If you believe there are errors or if you have questions or suggestions, please contact Garrett.\n\n' + \
        'Thanks!'

        outlook = Outlook()
        outlook.send_email(to=self.REPORT_RECIPIENTS,
                           cc=self.REPORT_CC,
                           subject=f'AMC Sweep Results - {self.TODAY_DATE}',
                           body=report_body,
                           from_account=self.REPORT_SENDER,
                           attachments=[self.OUTPUT_FILE],
                           auto_send=False)
