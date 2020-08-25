from   datalabs.etl.transform import TransformerTask


class FilenameStripperTransformerTask(TransformerTask):
    def _transform(self):
        return [datum for _, datum in self._parameters.data]
