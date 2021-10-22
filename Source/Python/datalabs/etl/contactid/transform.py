""" Contact ID assignment transformer. """
from bisect import bisect_left, insort_left
import csv
from   io import BytesIO
import logging
import random
import string

import numpy as np
import pandas

import datalabs.etl.transform as etl

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class ContactIDMergeTransformerTask(etl.TransformerTask):
    MAX_ID_ATTEMPTS = 10

    def _transform(self):
        sfmc_contacts, active_subscription, users, api_orders = self._to_dataframe()

        sfmc_contacts = self._assign_id_to_contacts(sfmc_contacts)

        users, sfmc_contacts = self._assign_id_to_users(users, sfmc_contacts)

        csv_data = [self._dataframe_to_csv(data) for data in [sfmc_contacts, active_subscription, users, api_orders]]

        return [data.encode('utf-8', errors='backslashreplace') for data in csv_data]

    def _to_dataframe(self):
        seperators = [',', ',', ',', ',']
        encodings_list = ['utf-8','utf-8','utf-8','utf-8' ]
        #NOTE: HADI, remove the next line
        LOGGER.debug(self._parameters.keys())

        return [
            pandas.read_csv(BytesIO(data), sep=seperator, encoding = encodings, dtype = 'str', low_memory=False)
            for data, seperator, encodings in zip(self._parameters['data'], seperators, encodings_list)
        ]

    # pylint: disable=redefined-builtin
    def _assign_id_to_contacts(self, sfmc_contacts):
        id_list = []
        for index in sfmc_contacts.index:
            if sfmc_contacts['HSContact_ID'][index] != sfmc_contacts['HSContact_ID'][index]:
                contact_id = self._get_new_id(id_list, sfmc_contacts['HSContact_ID'])
                sfmc_contacts['HSContact_ID'][index] = contact_id

        return sfmc_contacts

    @classmethod
    def _get_new_id(cls, id_list, existing_ids):
        found_id = True
        attempts = 0

        while found_id and attempts <= cls.MAX_ID_ATTEMPTS:
            contact_id = cls._generate_id()
            found_id = cls._find_id(id_list, contact_id, existing_ids)
            attempts += 1

        if attempts > cls.MAX_ID_ATTEMPTS:
            raise ValueError(
                f'The maximum number of attempts ({cls.MAX_ID_ATTEMPTS}) to '
                f'generate a new, unique contact ID was exceeded.',
            )

        return contact_id

    @classmethod
    def _generate_id(cls, size=15, chars=string.ascii_uppercase + string.ascii_lowercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))

    @classmethod
    def _find_id(cls, id_list, contact_id, existing_ids):
        index = bisect_left(id_list, contact_id)
        found = False

        if index != len(id_list) and id_list[index] == contact_id:
            pass
        elif contact_id in existing_ids:
            pass
        else:
            insort_left(id_list, contact_id, lo=0, hi=len(id_list))
            found = True

        return found

    def _assign_id_to_users(self, users, contacts):
        email_counts = []
        id_list = []
        empty = []
        users.insert(0, 'HSContact_ID', np.nan)
        for index_users in users.index:
            LOGGER.info(index_users)

            email_counts = self._count_instances_of_users_email_present_in_flatfile(index_users, contacts, users)

            if email_counts.size >= 1:
                if str(contacts['NAME'][email_counts[0]]).lower() == 'nan':

                    self._assign_users_contact_same_id_as_flatfile(index_users, email_counts, contacts, users)

                    self._copy_contact_name_from_users_to_flatfile(index_users, email_counts, contacts, users)

                    self._assign_flatfile_the_source_datalabs(email_counts, contacts)

                elif (str(users['FIRST_NM'][index_users]) + " " + str(users['LAST_NM'][index_users])).lower() == str(
                        contacts['NAME'][email_counts[0]]).lower():

                    self._assign_users_contact_same_id_as_flatfile(index_users, email_counts, contacts, users)

                elif str(users['FIRST_NM'][index_users]).lower() == 'nan' and str(
                        users['LAST_NM'][index_users]).lower() == 'nan':

                    self._assign_users_contact_same_id_as_flatfile(index_users, email_counts, contacts, users)

                else:
                    self._assign_users_contact_same_id_as_flatfile(index_users, email_counts, contacts, users)

            elif email_counts.size == 0:
                self._assign_new_id_to_users(index_users, users, id_list, empty)
                self._add_contact_from_users_to_flatfile(index_users, contacts, users)

        return users, contacts

    @classmethod
    def _count_instances_of_users_email_present_in_flatfile(cls, index_users, contacts, users):
        count = np.where(contacts['BEST_EMAIL'].astype(str).str.contains(users['EMAIL'][index_users]))[0]

        return count

    @classmethod
    def _copy_contact_name_from_users_to_flatfile(cls, index_users, email_counts, contacts, users):
        contact_name = str(users['FIRST_NM'][index_users]) + " " + str(users['LAST_NM'][index_users])

        contacts['NAME'][email_counts[0]] = contact_name

    @classmethod
    def _assign_flatfile_the_source_datalabs(cls, email_counts, contacts):
        contacts['SOURCE_ORD'][email_counts[0]] = 'DL'

    @classmethod
    def _assign_users_contact_same_id_as_flatfile(cls, index_users, email_counts, contacts, users):
        users['HSContact_ID'][index_users] = contacts['HSContact_ID'][email_counts[0]]

    @classmethod
    def _assign_new_id_to_users(cls, index_users, users, id_list, empty):
        contact_id = cls._get_new_id(id_list, empty)
        users['HSContact_ID'][index_users] = contact_id

    @classmethod
    def _add_contact_from_users_to_flatfile(cls, index_users, contacts, users):
        name = str(users['FIRST_NM'][index_users]) + " " + str(users['LAST_NM'][index_users])
        contacts = contacts.append({'HSContact_ID': users['HSContact_ID'][index_users], 'NAME': name,
                                    'BEST_EMAIL': users['EMAIL'][index_users],
                                    'ADDR1': users['ADDRESS_LINE_1'][index_users],
                                    'ADDR2': users['ADDRESS_LINE_2'][index_users], 'CITY': users['CITY'][index_users],
                                    'STATE': users['STATE'][index_users], 'ZIP': users['ZIPCODE'][index_users],
                                    'BUSNAME': users['ORG_NAME'][index_users], 'BUSTITLE': users['TITLE'][index_users],
                                    'SOURCE_ORD': 'DL',
                                    'RECSEQ': str(int(contacts['RECSEQ'][contacts.tail(1).index.item()])+1)},
                                    ignore_index=True)

    @classmethod
    def _dataframe_to_csv(cls, data):
        return data.to_csv(index=False, quoting=csv.QUOTE_NONNUMERIC)
