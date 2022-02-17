""" source: datalabs.etl.cpt.api.transform """
from datetime import date
import logging

import pandas
import pytest

from   datalabs.etl.cpt.api.transform import ReleasesTransformerTask

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


# pylint: disable=protected-access, redefined-outer-name
def test_get_correct_number_of_unique_release_dates_from_history(code_history):
    non_pla_releases, pla_releases = ReleasesTransformerTask._get_unique_dates_from_history(code_history)

    assert len(non_pla_releases) == 2
    assert len(pla_releases) == 4


# pylint: disable=protected-access, redefined-outer-name
def test_get_correct_unique_release_dates_from_history(code_history, expected_releases):
    non_pla_release_dates, pla_release_dates = ReleasesTransformerTask._get_unique_dates_from_history(code_history)
    non_pla_expected_releases = expected_releases.loc[~expected_releases.type.str.startswith('PLA')]
    pla_expected_releases = expected_releases.loc[expected_releases.type.str.startswith('PLA')]

    for effective_date in non_pla_expected_releases.effective_date:
        assert effective_date in non_pla_release_dates

    for effective_date in pla_expected_releases.effective_date:
        assert effective_date in pla_release_dates


# pylint: disable=protected-access, redefined-outer-name
def test_non_pla_release_types_are_correct(release_schedules):
    assert ReleasesTransformerTask._get_release_type(date(2264, 1, 1), release_schedules) == 'ANNUAL'

    assert ReleasesTransformerTask._get_release_type(date(2264, 8, 1), release_schedules) == 'OTHER'


# pylint: disable=protected-access, redefined-outer-name
def test_pla_release_types_are_correct(release_schedules):
    assert ReleasesTransformerTask._get_release_type(date(2264, 1, 1), release_schedules, "PLA-") == 'PLA-Q4'

    assert ReleasesTransformerTask._get_release_type(date(2264, 4, 1), release_schedules, "PLA-") == 'PLA-Q1'

    assert ReleasesTransformerTask._get_release_type(date(2264, 7, 1), release_schedules, "PLA-") == 'PLA-Q2'

    assert ReleasesTransformerTask._get_release_type(date(2264, 10, 1), release_schedules, "PLA-") == 'PLA-Q3'


# pylint: disable=protected-access, redefined-outer-name
def test_non_pla_publish_dates_are_correct(release_schedules):
    assert ReleasesTransformerTask._get_publish_date(date(2264, 1, 1), release_schedules) == date(2263, 9, 1)

    assert ReleasesTransformerTask._get_publish_date(date(2264, 8, 1), release_schedules) == date(2264, 8, 1)


# pylint: disable=protected-access, redefined-outer-name
def test_pla_publish_dates_are_correct(release_schedules):
    assert ReleasesTransformerTask._get_publish_date(date(2264, 1, 1), release_schedules, "PLA-") == date(2263, 10, 1)

    assert ReleasesTransformerTask._get_publish_date(date(2264, 4, 1), release_schedules, "PLA-") == date(2264, 1, 1)

    assert ReleasesTransformerTask._get_publish_date(date(2264, 7, 1), release_schedules, "PLA-") == date(2264, 4, 1)

    assert ReleasesTransformerTask._get_publish_date(date(2264, 10, 1), release_schedules, "PLA-") == date(2264, 7, 1)


# pylint: disable=protected-access, redefined-outer-name
def test_generated_release_ids_are_correct(expected_releases):
    release_ids = expected_releases.apply(
        lambda r: ReleasesTransformerTask._generate_release_id(
            r.effective_date,
            r.publish_date
        ),
        axis=1
    )

    assert all(release_ids == expected_releases.id)


# pylint: disable=protected-access, redefined-outer-name
def test_generated_releases_are_correct(code_history, release_schedules, expected_releases):
    releases = ReleasesTransformerTask._generate_release_table(code_history, release_schedules)

    assert all(expected_releases.type == releases.type)
    assert all(expected_releases.publish_date == releases.publish_date)
    assert all(expected_releases.effective_date == releases.effective_date)
    assert all(expected_releases.id == releases.id)


@pytest.fixture
def code_history():
    return pandas.DataFrame(
        dict(
            date=['20210101', '20210401', '20210701', '20210812', '20211001', '20220101', '20220101'],
            change_type=['ADDED', 'ADDED', 'ADDED', 'ADDED', 'ADDED', 'ADDED', 'ADDED'],
            concept_id=['1036624', '1036639', '1036675', '1036914', '1036816', '1036845', '1036845'],
            cpt_code=['0227U', '0242U', '0248U', '0003A', '0284U', '98980', '98981'],
            level=['', '', '', '', '', '', ''],
            prior_value=['', '', '', '', '', '', ''],
            current_value=['', '', '', '', '', '', ''],
            instruction=['', '', '', '', '', '', '']
        )
    )


@pytest.fixture
def release_schedules():
    return pandas.DataFrame(
        dict(
            type=['ANNUAL', 'OTHER', 'PLA-Q1', 'PLA-Q2', 'PLA-Q3', 'PLA-Q4'],
            effective_day=[1, 0, 1, 1, 1, 1],
            effective_month=['Jan', 'ANY', 'Apr', 'Jul', 'Oct', 'Jan'],
            publish_day=[1, 0, 1, 1, 1, 1],
            publish_month=['Sep', 'ANY', 'Jan', 'Apr', 'Jul', 'Oct']
        )
    )


@pytest.fixture
def expected_releases():
    ''' Expected release data with IDs calculcated as follows (pseudo-code):
        id = publish_date + (publish_date - effective_date).days
    '''

    return pandas.DataFrame(
        dict(
            id=[20200909, 20210011, 20210310, 20210812, 20210609, 20210779],
            type=['PLA-Q4', 'PLA-Q1', 'PLA-Q2', 'OTHER', 'PLA-Q3', 'ANNUAL'],
            effective_date=[
                date(2021, 1, 1), date(2021, 4, 1), date(2021, 7, 1), date(2021, 8, 12),
                date(2021, 10, 1), date(2022, 1, 1)
            ],
            publish_date=[
                date(2020, 10, 1), date(2021, 1, 1), date(2021, 4, 1), date(2021, 8, 12),
                date(2021, 7, 1), date(2021, 9, 1)]
        )
    )
