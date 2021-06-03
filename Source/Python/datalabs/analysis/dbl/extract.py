from dataclasses import dataclass
from datalabs.etl.sftp.extract import SFTPFileExtractorParameters, SFTPFileExtractorTask


# DBLReportFilesExtractorParameters = SFTPFileExtractorParameters(
#     base_path='',
#     files=','.join(
#         [
#             'changefileaudit.txt',
#             'ReportByFieldFrom_SAS.txt',
#             'countofchangesbyfieldextract.txt',
#             'recordactionextract.txt',
#             'changerecordcount.txt',
#             'PE_counts.txt',
#             'topbyPEcounts.txt',
#             'PrimSpecbyMPA.txt',
#             'SecSpecbyMPA.txt'
#         ]
#     ),
#     host='efttest.ama-assn.org',
#     username='datalabsstst',
#     password=''
# )
#
# DBLReportFilesExtractor = SFTPFileExtractorTask(DBLReportFilesExtractorParameters.__dict__)
# DBLReportFilesExtractor.run()


@dataclass
# pylint: disable=too-many-instance-attributes
class DBLTextDataExtractorParameters:
    base_path: str
    files: str
    host: str
    username: str
    password: str
    execution_time: str = None
    include_names: str = None
    data: object = None


class DBLTextDataExtractor(SFTPFileExtractorTask):
    PARAMETER_CLASS = DBLTextDataExtractorParameters
