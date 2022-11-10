''' CPT release data transformers. '''
import pandas

from   datalabs.etl.cpt.release.type import RELEASE_TYPES
from   datalabs.etl.csv import CSVWriterMixin
from   datalabs.task import Task


class ReleaseTypesTransformerTask(CSVWriterMixin, Task):
    def run(self) -> 'Transformed Data':
        release_types = pandas.DataFrame(data=RELEASE_TYPES)

        return [self._dataframe_to_csv(release_types)]
