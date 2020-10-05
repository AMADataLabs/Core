"""Oneview PPD Loader Task"""
import logging

from datalabs.etl.load import LoaderTask
from datalabs.etl.task import ETLException
from datalabs.etl.load import ConsoleLoaderTask
from datalabs.etl.fs import LocalUnicodeTextFileLoaderTask
from datalabs.etl.s3 import S3UnicodeTextFileLoaderTask

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


class PPDLocalFileLoader(LoaderTask):
    def _load(self):
        try:
            for datum in self._parameters.data:
                self._logger.info(datum)
        except:
            self._logger.info(self._parameters.data)
