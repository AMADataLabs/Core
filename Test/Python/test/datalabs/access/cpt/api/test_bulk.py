""" source: datalabs.access.cpt.api.bulk """
from   datetime import datetime, timezone, timedelta

from   datalabs.access.cpt.api.bulk import FilesEndpointTask


# pylint: disable=redefined-outer-name, protected-access
def test_get_authorized_years_with_explicit_cptapi_year():
    authorizations = dict(CPTAPI19=dict(start="2019-01-01T00:00:00-05:00", end="2468-10-11T00:00:00-05:00"))

    authorized_years = FilesEndpointTask._get_authorized_years(authorizations)

    assert len(authorized_years) == 1
    assert authorized_years[0] == 2019


# pylint: disable=redefined-outer-name, protected-access
def test_get_authorized_years_with_explicit_cptcs_year():
    authorizations = dict(CPTCS19=dict(start="2019-01-01T00:00:00-05:00", end="2468-10-11T00:00:00-05:00"))

    authorized_years = FilesEndpointTask._get_authorized_years(authorizations)

    assert len(authorized_years) == 1
    assert authorized_years[0] == 2019


# pylint: disable=redefined-outer-name, protected-access
def test_get_authorized_years_with_cptcs_product_code():
    start_time = datetime.now(timezone.utc) - timedelta(days=1)
    start_timestamp = start_time.isoformat(sep='T')
    authorizations = dict(CPTCS=dict(start=start_timestamp, end="2468-12-31T23:59:59"))

    authorized_years = FilesEndpointTask._get_authorized_years(authorizations)

    assert len(authorized_years) == 1
    assert authorized_years[0] == start_time.year


# pylint: disable=redefined-outer-name, protected-access
def test_get_authorized_years_with_implicit_cptapi_year():
    start_time = datetime.now(timezone.utc) - timedelta(days=1)
    start_timestamp = start_time.isoformat(sep='T')
    authorizations = dict(CPTAPI=dict(start=start_timestamp, end="2468-12-31T23:59:59"))

    authorized_years = FilesEndpointTask._get_authorized_years(authorizations)

    assert len(authorized_years) == 1
    assert authorized_years[0] == start_time.year


# pylint: disable=redefined-outer-name, protected-access
def test_get_authorized_years_with_expired_entitlement():
    start_timestamp = "2022-01-01T00:00:00-05:00"
    start_time = datetime.fromisoformat(start_timestamp)
    product_code = f"CPTCS{start_time.year - int(start_time.year / 100) * 100}"
    authorizations = {product_code: dict(start=start_timestamp, end="2022-12-31T23:59:59+00:00")}

    authorized_years = FilesEndpointTask._get_authorized_years(authorizations)

    assert len(authorized_years) == 0


# pylint: disable=redefined-outer-name, protected-access
def test_get_authorized_years_handles_old_expiration_date_format():
    authorizations = dict(CPTCS19=dict(start="1945-01-11T00:00:00-05:00", end="2468-10-11T00:00:00-05:00"))

    authorized_years = FilesEndpointTask._get_authorized_years(authorizations)

    assert len(authorized_years) == 1
    assert authorized_years[0] == 2019


# pylint: disable=redefined-outer-name, protected-access
def test_get_authorized_years_handles_other_product_codes_with_cptcs_in_base():
    authorizations = dict(CPTCSP=dict(start="1945-01-11T00:00:00-05:00", end="2468-10-11T00:00:00-05:00"))

    authorized_years = FilesEndpointTask._get_authorized_years(authorizations)

    assert len(authorized_years) == 0
