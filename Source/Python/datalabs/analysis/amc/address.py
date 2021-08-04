""" Code for executing AMC address"""
from datetime import datetime
from io import BytesIO
import logging
import os
import string

import numpy as np
import pandas as pd

from datalabs.access import excel
from datalabs.analysis.amc.keywords import FALSE_POSITIVES, FLAGWORDS
import datalabs.feature as feature

if feature.enabled("WINDOWS"):
    from datalabs.access.aims import AIMS
    from datalabs.analysis.amc.sql import AMC_QUERY

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


# pylint: disable=too-many-locals, too-many-instance-attributes, invalid-name
class AMCAddressFlagger:
    def __init__(self):
        self._today_date = str(datetime.now().date())

        self._output_file_password = None

    def _get_flag_words(self):
        flag_words = pd.read_excel(self._flag_word_file, header=None)[0].values
        flag_words = [str(word).lower() for word in flag_words]

        return flag_words

    def flag(self, data: pd.DataFrame = None):
        if data is None and feature.enabled("WINDOWS"):
            LOGGER.info('Querying active amc-sourced address data.')
            data = self._get_amc_address_data()

        LOGGER.info('Cleaning data.')
        cleaned_data = self._clean_str_data(data)

        flagged_data, summary = self._get_flagged_data_and_summary(cleaned_data)

        report_body = \
            f"""
            Hello!

            Attached are the latest results of the AMC address flagging script.

            Results summary:
            {summary}

            This report and email were generated automatically
            If you believe there are errors or if you have questions or suggestions, please contact Garrett.
            """.strip().replace('    ', '')  # removes tab-spacing at beginning of each line in email body

        # BytesIO of Excel report
        report_data = self._save_output(flagged_data)
        # flagged_data.to_excel(report_data)  # unnecessary if using report_data = self._save_output(...)
        report_data.seek(0)
        # BytesIO of report summary text
        body_data = BytesIO()
        body_data.write(report_body)
        body_data.seek(0)

        LOGGER.info('Done creating report.')
        return [report_data, body_data]

    # if running locally
    def _get_amc_address_data(self):
        address_data = None

        if feature.enabled("WINDOWS"):
            with AIMS() as aims:
                data = aims.read(sql=AMC_QUERY, coerce_float=False)

            address_data = self._clean_str_data(data)

        return address_data

    def _clean_str_data(self, data: pd.DataFrame):
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

        return data.drop_duplicates()

    def _get_flagged_data_and_summary(self, data):
        LOGGER.info('\tAdding flag indicator columns:')
        LOGGER.info('\t\taddr1')
        data['addr1_flagged'] = data['addr_line1'].apply(self._is_flagged_address_line_1)
        LOGGER.info('\t\taddr2')
        data['addr2_flagged'] = data['addr_line2'].apply(self._is_flagged_address_line_2)
        LOGGER.info('\t\tcity')
        data['city_flagged'] = data['city_cd'].apply(self._is_flagged_city)
        LOGGER.info('\t\tstate')
        data['state_flagged'] = data['state_cd'].apply(self._is_flagged_state)
        LOGGER.info('\t\tzip')
        data['zip_flagged'] = data['zip'].apply(self._is_flagged_zip)

        LOGGER.info('\t\tflagwords')
        data['contains_flag_word'] = data['address'].apply(self._contains_flagword)

        data.drop_duplicates(inplace=True)
        LOGGER.info('\tGetting flag type counts.')

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
        LOGGER.info('\tCompiling flagged Records.')
        any_flags = []
        for _, row in data.iterrows():
            a = any([row['addr1_flagged'],
                     row['addr2_flagged'],
                     row['city_flagged'],
                     row['state_flagged'],
                     row['zip_flagged'],
                     row['contains_flag_word']])
            any_flags.append(a)

        data['any_flag'] = any_flags
        results_summary = ''
        results_summary += f"\nCount of all flagged amc-sourced addresses: {len(data[data['any_flag']])}"
        results_summary += '\nFlagging summary: (addresses can be flagged by multiple fields, ' \
                           'so the sum of these counts may exceed count above)'
        for f in flags:
            count = flags[f]
            if count > 0:
                results_summary += f'\n\t{f}: {count}'

        data.drop(columns='address', axis=1, inplace=True)  # delete temp column

        flagged_data = data[data['any_flag']]
        flagged_data['date_checked'] = self._today_date
        flagged_data.drop_duplicates(inplace=True)

        return flagged_data, results_summary

    def _save_output(self, data: pd.DataFrame) -> BytesIO:
        data.drop_duplicates(inplace=True)
        file = BytesIO()
        file = excel.save_formatted_output(data, file, 'AMC Address Sweep')
        # excel.add_password_to_xlsx(self._output_file, self._output_file_password)  # can only do on Windows?
        return file

    @classmethod
    def _is_flagged_city(cls, city_string):
        city_string = city_string.lower()
        return any(
            [
                city_string == '',
                not cls._contains_n_unique_chars(city_string, 2),
                cls._contains_any_digits(city_string)
            ]
        )

    @classmethod
    def _is_flagged_address_line_1(cls, text, flag_null=False):
        flag = False
        if not flag_null:
            if text is not None and len(text) != 0:
                text = text.lower()
                if not cls._contains_n_unique_chars(text, 2):
                    flag = True
        else:
            if text is None or len(text) == 0 or text == '':
                flag = True
        return flag

    @classmethod
    def _is_flagged_address_line_2(cls, text):
        flag = False
        if text is None or \
                len(text) == 0 or \
                not cls._contains_n_unique_chars(text, 2) or text.isdigit():
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

    def _contains_flagword(self, address_string):
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

        return any(t in FLAGWORDS for t in tokens)
