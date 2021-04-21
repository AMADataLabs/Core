from   abc import ABC, abstractmethod
from   io import BytesIO

import csv
import logging
import pandas
import numpy as np
import pdb
import random
import string
from bisect import bisect_left, insort_left

import datalabs.etl.transform as etl

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)

class ContactIDMergeTransformerTask(etl.TransformerTask, ABC):
    def _transform(self):
        pdb.set_trace()
        sfmc_contacts, active_subscription, users, api_orders = self._to_dataframe()

        sfmc_contacts = self._assign_id_to_contacts(sfmc_contacts)

        users, sfmc_contacts = self._assign_id_to_users(users, sfmc_contacts)

        LOGGER.info(sfmc_contacts.head(2))

        csv_data = [self._dataframe_to_csv(data) for data in [sfmc_contacts, active_subscription, users, api_orders]]

        return [data.encode('utf-8', errors='backslashreplace') for data in csv_data]

    def _to_dataframe(self):
        seperators = ['\t', ',', ',', ',']
        encodings_list = ['ISO 8859-1','utf-8','utf-8','utf-8' ]
        return [pandas.read_csv(BytesIO(data), sep=seperator, encoding = encodings, dtype = 'str', low_memory=False) for data, seperator, encodings in zip(self._parameters['data'], seperators, encodings_list)]


    def _assign_id_to_contacts(self, contacts):
        id_list = []
        for ind in contacts.index:
            if contacts['HSContact_ID'][ind] != contacts['HSContact_ID'][ind]:
                id = id_check(id_list, contacts['HSContact_ID'])
                contacts['HSContact_ID'][ind] = id
        return contacts


    def id_check(id_list, existing_ids):
        x = id_generator()
        while True:
            id = BinarySearch(id_list, x, existing_ids)
            if id != 'nan':
                return id
                break

    def id_generator(size=15, chars=string.ascii_uppercase + string.ascii_lowercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))

    def BinarySearch(id_list, x, existing_ids):
        i = bisect_left(id_list, x)
        if i != len(id_list) and id_list[i] == x:
            return 'nan'
        elif x in existing_ids:
            print('yes')
            return 'nan'
        else:
            insort_left(id_list, x, lo=0, hi=len(id_list))
            return x

    def _assign_id_to_users(users, contacts):
        a = []
        id_list = []
        empty = []
        users.insert(0, 'HSContact_ID', np.nan)
        for index_users in users.index:
            print(index_users)

            a = check_if_users_email_present_in_flatfile(index_users)

            if a.size >= 1:
                if str(contacts['NAME'][a[0]]).lower() == 'nan':

                    assign_users_contact_same_id_as_flatfile(index_users, a)

                    copy_contact_name_from_users_to_flatfile(index_users, a)

                    assign_flatfile_the_source_datalabs(a)

                elif (str(users['FIRST_NM'][index_users]) + " " + str(users['LAST_NM'][index_users])).lower() == str(
                        contacts['NAME'][a[0]]).lower():

                    assign_users_contact_same_id_as_flatfile(index_users, a)

                elif str(users['FIRST_NM'][index_users]).lower() == 'nan' and str(
                        users['LAST_NM'][index_users]).lower() == 'nan':

                    assign_users_contact_same_id_as_flatfile(index_users, a)

                else:
                    assign_users_contact_same_id_as_flatfile(index_users, a)

            elif a.size == 0:
                assign_new_id_to_users(index_users)
                add_contact_from_users_to_flatfile(index_users)

        return users, contacts

    def check_if_users_email_present_in_flatfile(index_users):
        global contacts
        count = np.where(contacts['BEST_EMAIL'].astype(str).str.contains(users['EMAIL'][index_users]))[0]
        return count

    def copy_contact_name_from_users_to_flatfile(index_users, a):
        global contacts
        contacts['NAME'][a[0]] = str(users['FIRST_NM'][index_users]) + " " + str(users['LAST_NM'][index_users])

    def assign_flatfile_the_source_datalabs(a):
        global contacts
        contacts['SOURCE_ORD'][a[0]] = 'DL'

    def assign_users_contact_same_id_as_flatfile(index_users, a):
        global users
        users['HSContact_ID'][index_users] = contacts['HSContact_ID'][a[0]]

    def assign_new_id_to_users(index_users):
        global users
        id = id_check(id_list, empty)
        users['HSContact_ID'][index_users] = id

    def add_contact_from_users_to_flatfile(index_users):
        global contacts
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

