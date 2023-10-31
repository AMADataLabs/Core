""" CPT authorization mix-in and product code constants. """
from   datetime import datetime, timezone
from   enum import Enum


class ProductCode(Enum):
    CODE_SET = "CPTCS"
    KNOWLEDGE_BASE = "CPTKB"
    VIGNETTES = "CPTV"


class AuthorizedAPIMixin:
    @classmethod
    def _authorized(cls, authorizations, requested_year):
        authorized_years = cls._get_authorized_years(authorizations)
        authorized = False

        if requested_year in authorized_years:
            authorized = True

        return authorized

    @classmethod
    def _get_authorized_years(cls, authorizations):
        '''Get year from authorizations which are of the form:
            {PRODUCT_CODE}YY: ISO-8601 Timestamp
           For example,
            {PRODUCT_CODE}23: 2023-10-11T00:00:00-05:00
        '''
        cpt_api_authorizations = {key:value for key, value in authorizations.items() if cls._is_cpt_product(key)}
        current_time = datetime.now(timezone.utc)
        authorized_years = []

        for product_code, period_of_validity in cpt_api_authorizations.items():
            authorized_years += cls._generate_authorized_years(product_code, period_of_validity, current_time)

        return authorized_years

    @classmethod
    def _is_cpt_product(cls, product):
        return product.startswith(cls.PRODUCT_CODE.value)

    @classmethod
    def _generate_authorized_years(cls, product_code, period_of_validity, current_time):
        period_of_validity["start"] = datetime.fromisoformat(period_of_validity["start"]).astimezone(timezone.utc)
        period_of_validity["end"] = datetime.fromisoformat(period_of_validity["end"]).astimezone(timezone.utc)
        authorized_years = []

        if (
            product_code != cls.PRODUCT_CODE.value
            and product_code.startswith(cls.PRODUCT_CODE.value)
            and current_time >= period_of_validity["start"] <= current_time <= period_of_validity["end"]
        ):
            authorized_years += cls._generate_years_from_product_code(cls.PRODUCT_CODE.value, product_code)

        return authorized_years

    @classmethod
    def _generate_years_from_period(cls, period, current_time):
        years = list(range(period["start"].year, current_time.year + 1))

        if period["end"] <= current_time:
            years.pop()

        return years

    @classmethod
    def _generate_years_from_product_code(cls, base_product_code, product_code):
        authorized_years = []

        try:
            authorized_years.append(cls._parse_authorization_year(base_product_code, product_code))
        except ValueError:
            pass

        return authorized_years

    def _list_files(self, prefix):
        files = []

        if self._parameters.bucket_base_path:
            prefix = self._parameters.bucket_base_path + prefix

        response = self._s3.list_objects_v2(Bucket=self._parameters.bucket_name, Prefix=prefix)

        if "Contents" in response:
            files = [x["Key"] for x in response["Contents"]]

        return files

    @classmethod
    def _parse_authorization_year(cls, base_product_code, product_code):
        two_digit_year = product_code[len(base_product_code):]

        return int('20' + two_digit_year)
