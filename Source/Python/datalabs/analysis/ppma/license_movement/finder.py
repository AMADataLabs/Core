""" License Movement PPMA Update Process """
# pylint: disable=import-error,logging-fstring-interpolation,undefined-variable,unused-import,bare-except,pointless-string-statement,unused-variable,protected-access,wildcard-import,invalid-name,trailing-whitespace

from datetime import datetime
import logging
import os
import pandas as pd

from pgeocode import GeoDistance

from datalabs.access.aims import AIMS
from datalabs.analysis.ppma.license_movement.sql_statements import *

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


class LicenseMovementFinder:
    def __init__(self):
        self.license_to_credentialing_address_distance_threshold = os.environ.get('LIC_TO_CRED_MAX_DISTANCE', 100)

        # license states for which we can't ingest the addresses from
        self.disallowed_states = [
            'CA',
            'DE',
            'MT',
            'NE',
            'NJ',
            'NY',
            'PA',
            'PR',
            'UT',
            'WA'
        ]

    @classmethod
    def get_license_ppma_mismatch_data(cls):
        with AIMS() as aims:
            data = pd.read_sql(sql=GET_LICENSE_PPMA_MISMATCH_DATA, con=aims._connection, coerce_float=False)
            LOGGER.info(f' - AIMS QUERY COMPLETE: {str(len(data))}')
            return data

    @classmethod
    def get_license_state_license_address_state_match_and_mismatch_data(cls, data: pd.DataFrame):
        LOGGER.info('FILTERING AIMS DATA TO MATCH/MISATCH STATE DATA')
        match = data[data['license_state'] == data['license_addr_state']]
        mismatch = data[data['license_state'] != data['license_addr_state']]
        LOGGER.info(f' - MATCH: {str(len(match))}')
        LOGGER.info(f' - MISMATCH: {str(len(mismatch))}')
        return match, mismatch

    @classmethod
    def filter_out_previous_ppma_addresses(cls, data: pd.DataFrame, address_data=None):
        """
        Strategy here is to isolate pairs of (entity_id, comm_id) where comm_id is license address for current data,
        and to find the (entity_id, comm_id) pairs for previous PPMA data, and to cut out the intersection.
        """
        if address_data is None:
            LOGGER.info('filter_out_previous_ppma_addresses')
            with AIMS() as aims:
                address_data = pd.read_sql(GET_PREVIOUS_PPMA_DATA, con=aims._connection, coerce_float=False)

        LOGGER.info(f'old_ppma_data: {str(len(address_data))}')
        data_reindexed = data.set_index(['entity_id', 'license_addr_comm_id'])
        address_data.set_index(['entity_id', 'previous_ppma_comm_id'], inplace=True)
        filtered = data_reindexed[~data_reindexed.index.isin(address_data.index)].reset_index()
        LOGGER.info(f'filtered: {str(len(filtered))}')
        return filtered

    @classmethod
    def filter_to_most_recent_license(cls, data: pd.DataFrame):
        LOGGER.info('FILTERING TO MOST RECENT LICENSE')
        pre_filter = len(data)
        data = data.sort_values(by='lic_issue_dt', ascending=False).groupby('entity_id').first().reset_index()
        post_filter = len(data)
        LOGGER.info(f'Removed {str(post_filter-pre_filter)} records by filtering to most recent license')
        return data

    def find_potential_updates(self, data=None, old_ppma_data=None):
        if data is None:
            LOGGER.info('QUERYING AIMS FOR LICENSE-PPMA MISMATCH DATA')
            data = self.get_license_ppma_mismatch_data()
            LOGGER.info(f'got base data: {str(len(data))}')
        match, mismatch = self.get_license_state_license_address_state_match_and_mismatch_data(data)

        for col in match.columns.values:
            match[col] = match[col].astype(str).apply(lambda x: x.strip())
        """
        match - the data in which license is newer than PPMA and in another state, 
                AND the addr state on license == PPMA state -> strong update potential
        mismatch - data in which license is newer than PPMA and in another state,
                AND the addr state on license != PPMA state -> this is the data which would follow to the "branch" in
                the flow chart, where we proceed to look for active licenses in the state of this observed 
                license address state
        """

        LOGGER.info(f'got match data: {str(len(match))}')
        if old_ppma_data is not None:
            match = self.filter_out_previous_ppma_addresses(match, address_data=old_ppma_data)
            LOGGER.info(f'got filtered data: {str(len(match))}')

        match = self.filter_to_most_recent_license(match)
        return match

    def filter_on_credentialing_zip_distance(self, data: pd.DataFrame, credentialing_data=None, ppd=None):
        LOGGER.info('FILTERING ON ZIP DISTANCE')
        LOGGER.info(f' - START: {str(len(data))}')

        credentialing_data = credentialing_data[['ME', 'ZIPCODE', 'FULL_DT']].drop_duplicates()
        credentialing_data.rename(columns={'ZIPCODE': 'CREDENTIALING_ZIP'}, inplace=True)

        ppd = ppd[['ME', 'ENTITY_ID']].drop_duplicates()

        # add entity_id from expanded ppd file
        ppd['ME'] = ppd['ME'].apply(lambda x: ('00000' + str(x))[-11:])  # pre-emptive cleanup
        credentialing_data['ME'] = credentialing_data['ME'].apply(lambda x: ('00000' + str(x))[-11:])
        credentialing_data = credentialing_data.merge(ppd, on='ME', how='inner')
        LOGGER.info(f'credentialing_data: {str(len(credentialing_data))}')

        credentialing_data['ENTITY_ID'] = credentialing_data['ENTITY_ID'].astype(str).apply(lambda x: x.strip())
        data['entity_id'] = data['entity_id'].astype(str).apply(lambda x: x.strip())
        # add ME so we can merge credentialing org address data to the potential license update data
        data = data.merge(
            credentialing_data,
            left_on='entity_id',
            right_on='ENTITY_ID',
            how='inner'
        )
        LOGGER.info(f'post-merge: {str(len(data))}')

        # get distances from credentialing org
        dist = GeoDistance(country='us', errors='error')
        LOGGER.info(' - CALCULATING PPMA AND LICENSE ADDRESS DISTANCES TO CREDENTIALING ORG ADDRESS')
        LOGGER.info(f' - PRE-DISTANCE-CALCULATION: {str(len(data))}')
        data['zip'] = data['zip'].astype(str).apply(lambda x: x.strip()[:5])
        data['ppma_zip'] = data['ppma_zip'].astype(str).apply(lambda x: x.strip()[:5])
        data['CREDENTIALING_ZIP'] = data['CREDENTIALING_ZIP'].astype(str).apply(lambda x: x.strip()[:5])

        data = data[~data['zip'].isna()]  # zip must exist to find dist
        data = data[~data['ppma_zip'].isna()]  # zip must exist to find dist
        data = data[~data['CREDENTIALING_ZIP'].isna()]  # zip must exist to find dist

        data = data[~data['zip'].apply(lambda x: x in ['', '0', 0])]
        data = data[~data['ppma_zip'].apply(lambda x: x in ['', '0', 0])]
        data = data[~data['CREDENTIALING_ZIP'].apply(lambda x: x in ['', '0', 0])]

        data['distance_ppma_to_cred_org'] = dist.query_postal_code(
            data['ppma_zip'].values,
            data['CREDENTIALING_ZIP'].values
        )
        data['distance_ppma_to_cred_org'] = data['distance_ppma_to_cred_org'] / 1.609344  # km to miles
        data['distance_lic_addr_to_cred_org'] = dist.query_postal_code(
            data['zip'].values,
            data['CREDENTIALING_ZIP'].values
        )
        data['distance_lic_addr_to_cred_org'] = data['distance_lic_addr_to_cred_org'] / 1.609344  # km to miles

        data.to_excel('data_pre_dist_filter.xlsx', index=False)

        LOGGER.info(f' - PRE-FILTER: {str(len(data))}')
        LOGGER.info(' - FILTERING TO CLOSER LICENSE ADDRESSES')
        """
        filter such that
         - distance between lic address and credentialing org address is no more than max dist AND 
         - EITHER of the following:
            - license address closer to cred org than ppma is
            - ppma is null (can't compare distances)
        """
        data = data[~data['distance_ppma_to_cred_org'].isna()]  # remove NA - usually result of addresses in provinces
        data = data[~data['distance_lic_addr_to_cred_org'].isna()]  # remove NA - same as above
        filtered_data = data[
            (
                data['distance_lic_addr_to_cred_org'] <= float(
                    self.license_to_credentialing_address_distance_threshold
                )
            ) &
            (
                data['distance_lic_addr_to_cred_org'] <= data['distance_ppma_to_cred_org'].astype(float)
            )
        ]

        LOGGER.info(f' - END: {str(len(filtered_data))}')
        if len(filtered_data) == 0:
            raise ValueError('Something has gone terribly wrong.')
        return filtered_data

    def filter_to_allowed_states(self, data: pd.DataFrame):
        LOGGER.info('FILTERING TO ALLOWED LICENSE STATES')
        LOGGER.info(f' - START: {str(len(data))}')
        # remove data for licenses from disallowed states
        data = data[~data['license_state'].isin(self.disallowed_states)]
        LOGGER.info(f' - END: {str(len(data))}')
        return data

    @classmethod
    def filter_to_valid_credentialing_data(cls, data: pd.DataFrame):
        LOGGER.info('FILTERING TO VALID CREDENTIALING DATA')
        LOGGER.info(f' - START: {str(len(data))}')
        # take most recent profile order
        data['FULL_DT'] = pd.to_datetime(data['FULL_DT'])
        data = data.sort_values(by='FULL_DT', ascending=False).groupby('ME').first().reset_index()

        # credentialing profile order occurs AFTER license issue date
        data['lic_issue_dt'] = pd.to_datetime(data['lic_issue_dt'])
        data['FULL_DT'] = pd.to_datetime(data['FULL_DT'])

        data = data[data['lic_issue_dt'] <= data['FULL_DT']]
        LOGGER.info(f' - END: {str(len(data))}')
        return data

    @classmethod
    def format_batch_load_file(cls, data: pd.DataFrame):
        LOGGER.info('FORMATTING BATCH LOAD FILE')
        batch_data = data[
            [
                'entity_id',
                'ME',
                'license_addr_comm_id',
                'addr_line0',
                'addr_line1',
                'addr_line2',
                'city_cd',
                'license_addr_state',
                'zip'
            ]
        ]
        batch_data.rename(
            columns={
                'ME': 'me',
                'license_addr_comm_id': 'comm_id',
                'addr_line2': 'addr_line_1',
                'addr_line1': 'addr_line_2',
                'addr_line0': 'addr_line_3',
                'city_cd': 'addr_city',
                'license_addr_state': 'addr_state',
                'zip': 'addr_zip',
            },
            inplace=True
        )
        # new columns
        batch_data['load_type_ind'] = 'R'
        batch_data['source'] = 'LIC-MVT'
        batch_data['source_dtm'] = str(datetime.now().date())
        batch_data['usage'] = 'PP'
        batch_data['type'] = 'N'
        batch_data['addr_plus4'] = ''  # required but empty
        batch_data['addr_country'] = ''  # required but empty

        ordered_cols = [
            'entity_id',
            'me',
            'comm_id',
            'usage',
            'load_type_ind',
            'addr_line_1',
            'addr_line_2',
            'addr_line_3',
            'addr_city',
            'addr_state',
            'addr_zip',
            'addr_plus4',
            'addr_country',
            'source',
            'source_dtm'
        ]

        formatted_data = pd.DataFrame()
        for col in ordered_cols:
            formatted_data[col] = batch_data[col]

        LOGGER.info(f'BATCH DATA: {str(len(formatted_data))}')
        return formatted_data
