''' CPT release data transformers. '''
from   dataclasses import dataclass
from   datetime import date, datetime
import json

from   dateutil.parser import isoparse
import pandas

from   datalabs.etl.cpt.release.type import RELEASE_TYPES
from   datalabs.etl.csv import CSVWriterMixin
from   datalabs.etl.transform import TransformerTask
from   datalabs.parameter import add_schema


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class ReleaseTransformerParameters:
    schedule: str
    execution_time: str


class ReleaseTransformerTask(CSVWriterMixin, TransformerTask):
    PARAMETER_CLASS = ReleaseTransformerParameters

    def _transform(self) -> 'Transformed Data':
        release_schedule = json.loads(self._parameters.schedule)
        release_date = isoparse(self._parameters.execution_time)

        release = self._generate_release_details(release_schedule, release_date)

        return [self._dataframe_to_csv(release)]

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

        return data

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


class ReleaseTypesTransformerTask(CSVWriterMixin, TransformerTask):
    def _transform(self) -> 'Transformed Data':
        release_types = pandas.DataFrame(data=RELEASE_TYPES)

        return [self._dataframe_to_csv(release_types)]
