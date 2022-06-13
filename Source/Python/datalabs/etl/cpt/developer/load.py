""" Email Report loader task """
from   dataclasses import dataclass

# pylint: disable=import-error, invalid-name
from   datalabs.etl.load import LoaderTask
from   datalabs.parameter import add_schema


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class EmailReportSMTPLoaderParameters:
    to: str
    data: list
    cc: str = None
    execution_time: str = None

class EmailReportSMTPLoaderTask(LoaderTask):
    PARAMETER_CLASS = EmailReportSMTPLoaderParameters

    def _load(self):
        pass
