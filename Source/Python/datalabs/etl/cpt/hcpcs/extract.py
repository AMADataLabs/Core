""" Extractor class for CPT standard release text data from the S3 ingestion bucket. """
from   dataclasses import dataclass
from   bs4 import BeautifulSoup

import requests

from   datalabs.parameter import add_schema
from   datalabs.task import Task
from dateutil.parser import isoparse


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class HCPCSParserParameters:
    include_names: str = None
    include_datestamp: str = None
    execution_time: str = None
    on_disk: str = False
    filter_future: str = False
    assume_role: str = None
    url: str = None


# pylint: disable=too-many-ancestors
class HCPCSQuarterlyUpdateReportURLExtractorTask(Task):
    PARAMETER_CLASS = HCPCSParserParameters

    def run(self):
        url_list = self._get_quarterly_update_report_urls(self._parameters.url)

        latest_url = self._select_latest_quarterly_update_report_url(url_list)

        return [latest_url.encode()]

    @classmethod
    def _get_quarterly_update_report_urls(cls, url):
        page = requests.get(url)
        soup = BeautifulSoup(page.content, "html.parser")

        return soup.find(id="block-cms-evo-content").find('ul').find_all("li")

    def _select_latest_quarterly_update_report_url(self, url_list):
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

        report = self._choose_report(reports)

        return report

    def _choose_report(self, report_dict):
        current_year_month = isoparse(self._parameters.execution_time).date().strftime('%Y%m')

        for key in list(report_dict.keys()):
            if key > current_year_month:
                del report_dict[key]

        latest_reports = list(dict(sorted(report_dict.items(), reverse=True)).values())

        return latest_reports[0]
