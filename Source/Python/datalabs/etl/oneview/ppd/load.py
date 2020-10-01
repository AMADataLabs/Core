"""Oneview PPD Loader Task"""

from datalabs.etl.load import LoaderTask
from datalabs.etl.task import ETLException
from datalabs.etl.fs import LocalUnicodeTextFileLoaderTask
from datalabs.etl.s3 import S3UnicodeTextFileLoaderTask


logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)

class PPDLocalFileLoader(LocalUnicodeTextFileLoaderTask):
    def _load(self):
