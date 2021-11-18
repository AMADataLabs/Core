""" Extractor class for CPT standard release text data from the S3 ingestion bucket. """
from   dataclasses import dataclass
from   bs4 import BeautifulSoup
from   datetime import datetime

import requests

from   datalabs.etl.extract import ExtractorTask
from   datalabs.parameter import add_schema


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class HCPCSParserParameters:
    include_names: str = None
    include_datestamp: str = None
    execution_time: str = None
    on_disk: str = False
    assume_role: str = None
    data: object = None
    url: str = None


# pylint: disable=too-many-ancestors
class HCPCSQuarterlyUpdateReportURLExtractorTask(ExtractorTask):
    PARAMETER_CLASS = HCPCSParserParameters

    def _extract(self):
        url_list = self._get_quarterly_update_report_urls(self._parameters.url)

        latest_url = self._select_latest_quarterly_update_report_url(url_list)

        return [latest_url.encode()]

    @classmethod
    def _get_quarterly_update_report_urls(cls, url):
        page = requests.get(url)
        soup = BeautifulSoup(page.content, "html.parser")

        return soup.find(id="block-cms-drupal-global-content").find('ul').find_all("li")

    @classmethod
    def _select_latest_quarterly_update_report_url(cls, url_list):
        reports = {}
        months = {
            'january': '01',
            'february': '02',
            'march': '03',
            'april': '04',
            'may': '05',
            'june': '06',
            'july': '07',
            'august': '08',
            'september': '09',
            'october': '10',
            'november': '11',
            'december': '12'
        }

        for report in url_list:
            url_suffix = report.find('a').get('href', '')
            url_split = url_suffix.replace('/files/zip/', '').split('-')
            year_month = url_split[1] + months[url_split[0].lower()]
            reports[year_month] = "https://www.cms.gov" + url_suffix

        reports = cls._filter_future_reports(reports)

        return reports[max(reports.keys())]


    @classmethod
    def _filter_future_reports(cls, report_dict):
        current_year_month = datetime.today().strftime('%Y%m')

        for key in list(report_dict.keys()):
            if key > current_year_month:
                del report_dict[key]

        return report_dict
