
import pandas as pd
from datalabs.access.aims import AIMS
from datalabs.analysis.ppma.license_movement.sql_statements import GET_LICENSE_PPMA_MISMATCH_DATA
import settings


class LicenseMovementFinder:
    @classmethod
    def get_license_ppma_mismatch_data(cls):
        with AIMS() as aims:
            data = pd.read_sql(sql=GET_LICENSE_PPMA_MISMATCH_DATA, con=aims._connection, coerce_float=False)
            return data

    @classmethod
    def get_license_state_license_address_state_match_and_mismatch_data(cls, data: pd.DataFrame):
        match = data[data['license_state'] == data['license_addr_state']]
        mismatch = data[data['license_state'] != data['license_addr_state']]
        return match, mismatch
