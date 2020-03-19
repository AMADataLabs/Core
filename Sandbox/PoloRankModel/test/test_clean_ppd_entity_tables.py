import logging
import os
from   pathlib import Path
import pytest
import sys

import datalabs.analysis.polo.rank.data.entity as entity_data
import datalabs.analysis.polo.rank.data.ppd as ppd_data

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


def test_standardize_datestamps_ignores_na_values(license_table):
    ppd_data.LicenseLtCleaner._standardize_datestamps(license_table, ['lic_exp_dt', 'lic_issue_dt', 'lic_rnw_dt'])

    assert 185 == len(license_table['lic_exp_dt'][license_table['lic_exp_dt'].isna()])
    assert 5 == len(license_table['lic_issue_dt'][license_table['lic_issue_dt'].isna()])
    assert 694 == len(license_table['lic_rnw_dt'][license_table['lic_rnw_dt'].isna()])


@pytest.fixture
def script_base_path():
    return  Path(__file__).parent


@pytest.fixture
def license_table(script_base_path):
    chunks = ppd_data.LicenseLtCleaner._read_csv_file_in_chunks(Path(script_base_path, 'license_lt_test.csv'))

    return next(chunks)
    pass
