" Oneview PPD Transformer"
import logging
import pandas

from datalabs.etl.transform import TransformerTask

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class PPDDataFrameToCSVText(TransformerTask):
    def _transform(self):
        dataframe = self._parameters.data
        return self._generate_csv_text(dataframe)

    def _generate_csv_text(self, dataframe):
        return pandas.to_csv(dataframe, columns = [])
