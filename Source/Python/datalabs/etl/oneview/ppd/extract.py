""" Oneview PPD Extractor from ods"""

# from   datalabs.access.jdbc import JDBC
# from   datalabs.etl.extract import ExtractorTask
#
#
# class PPDExtractorODS(JDBC, ExtractorTask):
#     def __init__(self):
#         self.query = '''SELECT * FROM ODS.ODS_PPD_FILE PE'''
#
#     def _extract(self):
#         with JDBC() as jdbc:
#             ppd = jdbc.read(self.query)
#
#         return ppd
