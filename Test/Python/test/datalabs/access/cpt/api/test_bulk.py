""" source: datalabs.access.cpt.api.bulk """
from   datetime import datetime, timezone

from   datalabs.access.cpt.api.bulk import FilesEndpointTask


# pylint: disable=redefined-outer-name, protected-access
def test_get_authorized_years_with_explicit_cptapi_year():
    authorizations = dict(CPTAPI19="2468-10-11T00:00:00-05:00")

    authorized_years = FilesEndpointTask._get_authorized_years(authorizations)

    assert len(authorized_years) == 1
    assert authorized_years[0] == 2019


# pylint: disable=redefined-outer-name, protected-access
def test_get_authorized_years_with_implicit_cptapi_year():
    authorizations = dict(CPTAPI="2468-10-11T00:00:00-05:00")
    current_time = datetime.now(timezone.utc)

    authorized_years = FilesEndpointTask._get_authorized_years(authorizations)

    assert len(authorized_years) == 1
    assert authorized_years[0] == current_time.year


# pylint: disable=redefined-outer-name, protected-access
def test_get_authorized_years_with_expired_entitlement():
    authorizations = dict(CPTAPI23="2022-10-11T00:00:00-05:00")

    authorized_years = FilesEndpointTask._get_authorized_years(authorizations)

    assert len(authorized_years) == 0
