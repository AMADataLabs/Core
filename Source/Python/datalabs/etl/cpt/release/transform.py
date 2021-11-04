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


class ReleaseTypesTransformerTask(CSVWriterMixin, TransformerTask):
    def _transform(self) -> 'Transformed Data':
        release_types = pandas.DataFrame(data=RELEASE_TYPES)

        return [self._dataframe_to_csv(release_types)]
