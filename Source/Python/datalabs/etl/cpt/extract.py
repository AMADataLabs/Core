""" Extractor class for CPT standard release text data from the S3 ingestion bucket. """
from   datetime import date, datetime
import json

import pandas

from datalabs.etl.s3.extract import S3WindowsTextExtractor


class CPTTextDataExtractor(S3WindowsTextExtractor):
    def extract(self):
        data = super().extract()
        release_date = self._extract_release_date()
        release_schedule = json.loads(self._configuration['RELEASE_SCHEDULE'])

        data.append(self._generate_release_types(release_schedule))
        data.append(self._generate_release_details(release_schedule, release_date))

        return data

    def _extract_release_date(self):
        latest_release_path = self._get_latest_path()
        release_datestamp = latest_release_path.rsplit('/', 1)[1]

        return datetime.strptime(release_datestamp, '%Y%m%d').date()

    def _generate_release_types(self, release_schedule):
        release_types = list(release_schedule.keys())

        release_types.append('OTHER')

        return pandas.DataFrame(dict(type=release_types))

    def _generate_release_details(self, release_schedule, release_date):
        release_type = self._get_release_type(release_schedule, release_date)
        effective_date = release_schedule[release_type][1]
        effective_date = date(release_date.year, effective_date.month, effective_date.day)

        return pandas.DataFrame(
            dict(
                publish_date=[release_date],
                effective_date=[effective_date],
                type=[release_type]
            )
        )

    def _get_release_type(self, release_schedule, release_date):
        release_date_for_lookup = date(1900, release_date.month, release_date.day)
        release_types = self._map_release_dates_to_types(release_schedule)

        return release_types.get(release_date_for_lookup, 'OTHER')

    def _map_release_dates_to_types(self, release_schedule):
        for release_type in release_schedule:
            release_schedule[release_type] = self._convert_datestamps_to_dates(release_schedule[release_type])

        return {dates[0]:type for type, dates in release_schedule.items()}

    @classmethod
    def _convert_datestamps_to_dates(cls, datestamps):
        return [datetime.strptime(datestamp, '%d-%b').date() for datestamp in datestamps]

