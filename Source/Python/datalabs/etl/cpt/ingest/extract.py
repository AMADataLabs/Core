""" Extractor class for CPT standard release text data from the S3 ingestion bucket. """
from   datetime import date, datetime
import json
import os

from   dateutil.parser import isoparse
import pandas

import datalabs.etl.s3.extract as extract


# pylint: disable=too-many-ancestors
class CPTTextDataExtractorTask(extract.S3UnicodeTextFileExtractorTask):
    def _extract(self):
        data = super()._extract()
        release_datestamp = self._get_execution_date() or self._extract_release_date()
        release_date = isoparse(release_datestamp).date()
        release_schedule = json.loads(self._parameters.variables['SCHEDULE'])
        release_source_path = os.path.join(self._parameters.variables['BASEPATH'], release_datestamp)

        data.insert(0, (release_source_path, self._generate_release_details(release_schedule, release_date)))

        return data

    def _extract_release_date(self):
        latest_release_path = self._get_latest_path()

        return latest_release_path.rsplit('/', 1)[1]

    @classmethod
    def _generate_release_types(cls, release_schedule):
        release_types = list(release_schedule.keys())

        release_types.append('OTHER')

        return pandas.DataFrame(dict(type=release_types))

    def _generate_release_details(self, release_schedule, release_date):
        release_type = self._get_release_type(release_schedule, release_date)
        effective_date = release_date

        if release_type != 'OTHER':
            effective_date = release_schedule[release_type][1]
            effective_date = date(release_date.year, effective_date.month, effective_date.day)

        data = pandas.DataFrame(
            dict(
                publish_date=[release_date],
                effective_date=[effective_date],
                type=[release_type]
            )
        )

        return data.to_csv(index=False)

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
