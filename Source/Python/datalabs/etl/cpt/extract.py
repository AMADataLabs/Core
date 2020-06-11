""" Extractor class for CPT standard release text data from the S3 ingestion bucket. """
from datetime import datetime
import pandas

from datalabs.etl.s3.extract import S3WindowsTextExtractor


class CPTTextDataExtractor(S3WindowsTextExtractor):
    def extract(self):
        data = super().extract()
        release_date = self._get_release_date()

        data.append(self._extract_release_type(release_date))
        data.append(self._extract_release_details(release_date))

        return data

    def _get_release_date(self):
        latest_release_path = self._get_latest_path()
        release_datestamp = latest_release_path.rsplit('/', 1)[1]

        return datetime.strptime(release_datestamp, '%Y%m%d').date()

    def _extract_release_type(self):
        release_schedule = self._configuration['RELEASE_SCHEDULE']

        for release_type in release_schedule:
            release_schedule[release_type] = self._convert_datestamps_to_dates(release_schedule[release_type])

    def _extract_release_details(self):
        pass

    @classmethod
    def _convert_datestamps_to_dates(cls, datestamps):
        return [datetime.strptime(datestamp, '%d-%b').date() for datestamp in datestamps]

