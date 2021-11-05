''' CPT release data transformers. '''
import pandas

from   datalabs.etl.cpt.release.type import RELEASE_TYPES
from   datalabs.etl.csv import CSVWriterMixin
from   datalabs.etl.transform import TransformerTask


class ReleaseTypesTransformerTask(CSVWriterMixin, TransformerTask):
    def _transform(self) -> 'Transformed Data':
        release_types = pandas.DataFrame(data=RELEASE_TYPES)

        return [self._dataframe_to_csv(release_types)]
