""" Extractor class for CPT standard release text data from the S3 ingestion bucket. """
from   datetime import date, datetime
from   dateutil.parser import isoparse
import json
import os

import pandas

import datalabs.etl.s3.extract as extract


class CPTTextDataExtractorTask(extract.S3UnicodeTextExtractorTask):
    def _extract(self):
        data = super()._extract()
        release_date = self._get_execution_date() or self._extract_release_date()
        release_schedule = json.loads(self._parameters.variables['SCHEDULE'])
        release_source_path = os.path.join(
            self._parameters.variables['PATH'], release_date.strftime('%Y%m%d')
        )

        data.insert(0, (release_source_path, self._generate_release_details(release_schedule, release_date)))

        return data

    def _get_execution_date(self):
        execution_time = self._parameters.variables.get('EXECUTION_TIME')
        execution_date = None

        if execution_time:
            execution_date = isoparse(execution_time).date()

        return execution_date

    def _extract_release_date(self):
        latest_release_path = self._get_latest_path()
        release_datestamp = latest_release_path.rsplit('/', 1)[1]

        return isoparse(release_datestamp).date()

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
