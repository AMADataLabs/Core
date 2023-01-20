""" AWS S3 Loader """
from   dataclasses import dataclass
from   io import BytesIO
import logging
import pickle

from   datalabs.etl.task import ExecutionTimeMixin
from   datalabs.parameter import add_schema
from   datalabs.task import Task
from   datalabs.tool.pdf import PDFSigner

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class PDFSigningTransformerParameters:
    credentials_password: str
    recipient: str
    execution_time: str=None


class PDFSigningTransformerTask(ExecutionTimeMixin, Task):
    PARAMETER_CLASS = PDFSigningTransformerParameters

    def run(self):
        credentials, packed_data = self._data
        named_files = pickle.loads(packed_data)

        named_pdfs = self._extract_pdfs(named_files)

        named_signed_pdfs = [self._sign_pdf(named_pdf, credentials) for named_pdf in named_pdfs]

        signed_files = list(self._replace_files(named_files, named_signed_pdfs))

        return [pickle.dumps(signed_files)]

    @classmethod
    def _extract_pdfs(cls, named_files):
        return [named_file for named_file in named_files if named_file[0].endswith('.pdf')]

    def _sign_pdf(self, named_pdf, credentials):
        unsigned_pdf_file = BytesIO(named_pdf[1])
        signed_pdf_file = BytesIO()
        credentials_file = BytesIO(credentials)
        password = self._parameters.credentials_password
        recipient = self._parameters.recipient

        PDFSigner.sign(unsigned_pdf_file, signed_pdf_file, credentials_file, password, recipient)

        return named_pdf[0], bytes(signed_pdf_file.getbuffer())

    @classmethod
    def _replace_files(cls, named_files, named_updated_files):
        named_updated_file_map = dict(named_updated_files)

        for name, file in named_files:
            if name in named_updated_file_map:
                yield (name, named_updated_file_map[name])
            else:
                yield (name, file)
