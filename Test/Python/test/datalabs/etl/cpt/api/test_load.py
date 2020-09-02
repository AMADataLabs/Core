""" source: datalabs.etl.cpt.extract """
from datetime import datetime, date
import logging

import pandas
import pytest

from   datalabs.etl.cpt.api.load import TableUpdater
import datalabs.model.cpt.api as model

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


# pylint: disable=protected-access
def test_columns_set_from_model_class():
    updater = TableUpdater(None, model.Code, None, None)

    assert all([column in updater._columns for column in ['code', 'modified_date', 'deleted']])


# pylint: disable=redefined-outer-name, protected-access
def test_get_current_data(current_codes):
    session = MockSession(current_codes)
    updater = TableUpdater(session, model.Code, None, None)

    current_models, current_data = updater._get_current_data()

    assert current_models == current_codes
    assert list(current_data.code) == ['21', '42', '84']


# pylint: disable=redefined-outer-name, protected-access
def test_differentiate_data_when_primary_key_not_equal_to_match_column(current_releases):
    session = MockSession(current_releases)
    updater = TableUpdater(session, model.Release, 'id', 'publish_date')
    _, current_data = updater._get_current_data()
    data = current_data.copy()
    data.loc[1] = [1, date(2100, 10, 1), date(2101, 1, 1), 'PLA-Q4']

    old_data, new_data = updater._differentiate_data(current_data, data)

    assert len(old_data) == 1
    assert list(old_data.type) == ['ANNUAL']
    assert len(new_data) == 1
    assert list(new_data.type) == ['PLA-Q4']


# pylint: disable=redefined-outer-name, protected-access
def test_differentiate_data_when_primary_key_equals_match_column(current_codes):
    session = MockSession(current_codes)
    updater = TableUpdater(session, model.Code, 'code', 'code')
    _, current_data = updater._get_current_data()
    data = current_data.copy()
    data.loc[3] = ['22', date(2100, 9, 1), False]
    data.loc[4] = ['44', date(2100, 10, 2), False]

    old_data, new_data = updater._differentiate_data(current_data, data)

    assert len(old_data) == 3
    assert list(old_data.code) == ['21', '42', '84']
    assert len(new_data) == 2
    assert list(new_data.code) == ['22', '44']


# pylint: disable=redefined-outer-name, protected-access
def test_filter_out_unchanged_data(old_codes):
    updater = TableUpdater(None, model.Code, 'code', 'code')

    changed_data = updater._filter_out_unchanged_data(old_codes)

    assert len(changed_data) == 1
    assert changed_data.deleted.iloc[0]


# pylint: disable=redefined-outer-name, protected-access
def test_get_matching_models(current_codes, old_codes):
    updater = TableUpdater(None, model.Code, 'code', 'code')
    current_codes.append(model.Code(code='22', modified_date=date(2100, 9, 1), deleted=False))
    current_codes.append(model.Code(code='44', modified_date=date(2100, 9, 1), deleted=False))

    models = updater._get_matching_models(current_codes, old_codes)
    codes = [model.code for model in models]

    assert len(models) == 3
    assert codes == ['21', '42', '84']


# pylint: disable=redefined-outer-name, protected-access
def test_update_models(current_codes, old_codes):
    session = MockSession(current_codes)
    updater = TableUpdater(session, model.Code, 'code', 'code')
    models = updater._get_matching_models(current_codes, old_codes)
    expected_dates = [date(1900, 10, 1), date(1900, 10, 1), date(1900, 10, 1)]
    expected_deleteds = [False, False, False]

    for model_, modified_date, deleted in zip(models, expected_dates, expected_deleteds):
        assert model_.modified_date == modified_date
        assert model_.deleted == deleted

    updater._update_models(models, old_codes)

    today = datetime.utcnow().date()
    expected_dates = [today, today, today]
    expected_deleteds[2] = True
    for model_, modified_date, deleted in zip(models, expected_dates, expected_deleteds):
        assert model_.modified_date == modified_date
        assert model_.deleted == deleted


# pylint: disable=redefined-outer-name, protected-access
def test_create_models(new_codes):
    updater = TableUpdater(None, model.Code, 'code', 'code')
    codes = new_codes.code.tolist()
    today = datetime.utcnow().date()

    models = updater._create_models(new_codes)

    assert len(models) == 3
    for code, model_ in zip(codes, models):
        assert model_.code == code
        assert model_.modified_date == today
        assert not model_.deleted


# pylint: disable=redefined-outer-name, protected-access
def test_add_models(new_codes):
    session = MockSession(new_codes)
    updater = TableUpdater(session, model.Code, 'code', 'code')
    models = updater._create_models(new_codes)

    updater._add_models(models)

    assert session.add_count == 3


class MockSession:
    def __init__(self, return_value):
        self._return_value = return_value
        self._add_count = 0

    @property
    def add_count(self):
        return self._add_count

    # pylint: disable=unused-argument
    def query(self, *args):
        return self

    def all(self):
        return self._return_value

    # pylint: disable=unused-argument
    def add(self, *args):
        self._add_count += 1


@pytest.fixture
def current_codes():
    return [
        model.Code(code='21', modified_date=date(1900, 10, 1), deleted=False),
        model.Code(code='42', modified_date=date(1900, 10, 1), deleted=False),
        model.Code(code='84', modified_date=date(1900, 10, 1), deleted=False),
    ]


@pytest.fixture
def current_releases():
    return [
        model.Release(id=0, publish_date=date(1900, 10, 1), effective_date=date(1901, 1, 1), type='ANNUAL'),
    ]


@pytest.fixture
def old_codes():
    return pandas.DataFrame(
        dict(
            code=['21', '42', '84'],
            deleted_CURRENT=[False, False, False],
            deleted=[False, False, True],
        )
    )


@pytest.fixture
def new_codes():
    return pandas.DataFrame(
        dict(
            code=['55', '66', '77'],
            deleted_CURRENT=[None, None, None],
            deleted=[False, False, False],
        )
    )
