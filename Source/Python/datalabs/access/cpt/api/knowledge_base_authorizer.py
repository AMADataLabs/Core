""" Release endpoint classes. """
import logging
from   datetime import datetime, timezone

from   datalabs.access.cpt.api.authorize import PRODUCT_CODE_KB

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


# pylint: disable=too-many-instance-attributes

def authorized(authorizations):
    authorized_years = get_authorized_years(authorizations)
    authorized = False
    code_set = get_current_year_code_set()
    if datetime.now().year in authorized_years:
        authorized = True

    return authorized


def get_current_year_code_set():
    return f'{PRODUCT_CODE_KB}{str(datetime.now().year)[2:]}'


def get_authorized_years(authorizations):
    '''Get year from authorizations which are of one of the form:
        {PRODUCT_CODE}YY: ISO-8601 Timestamp
       For example,
        {PRODUCT_CODE}23: 2023-10-11T00:00:00-05:00
    '''
    cpt_api_authorizations = {key: value for key, value in authorizations.items() if is_cpt_kb_product(key)}
    current_time = datetime.now(timezone.utc)
    authorized_years = []

    for product_code, period_of_validity in cpt_api_authorizations.items():
        authorized_years += generate_authorized_years(product_code, period_of_validity, current_time)

    return authorized_years


def is_cpt_kb_product(product):
    return product.startswith(PRODUCT_CODE_KB)


def generate_authorized_years(product_code, period_of_validity, current_time):
    period_of_validity["start"] = datetime.fromisoformat(period_of_validity["start"]).astimezone(timezone.utc)
    period_of_validity["end"] = datetime.fromisoformat(period_of_validity["end"]).astimezone(timezone.utc)
    authorized_years = []

    if (
            product_code.startswith(PRODUCT_CODE_KB)
            and current_time >= period_of_validity["start"] <= current_time <= period_of_validity["end"]
    ):
        authorized_years += generate_years_from_product_code(PRODUCT_CODE_KB, product_code)

    return authorized_years


def generate_years_from_period(period, current_time):
    years = list(range(period["start"].year, current_time.year + 1))

    if period["end"] <= current_time:
        years.pop()

    return years


def generate_years_from_product_code(base_product_code, product_code):
    authorized_years = []

    try:
        authorized_years.append(parse_authorization_year(base_product_code, product_code))
    except ValueError:
        pass

    return authorized_years


def parse_authorization_year(base_product_code, product_code):
    two_digit_year = product_code[len(base_product_code):]

    return int('20' + two_digit_year)
