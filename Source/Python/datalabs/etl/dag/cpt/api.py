''' DAG definition for the DAG Scheduler. '''
from   datalabs.etl.dag.dag import DAG, register
from   datalabs.etl.archive.transform import UnzipTransformerTask, ZipTransformerTask
from   datalabs.etl.cpt.release.transform import ReleaseTypesTransformerTask
from   datalabs.etl.cpt.api.transform import \
    CodesTransformerTask, \
    ShortDescriptorTransformerTask, \
    MediumDescriptorTransformerTask, \
    LongDescriptorTransformerTask, \
    ModifierTypeTransformerTask, \
    ModifierTransformerTask, \
    ConsumerDescriptorTransformerTask, \
    ClinicianDescriptorTransformerTask, \
    ClinicianDescriptorCodeMappingTransformerTask, \
    PLADetailsTransformerTask, \
    ManufacturerTransformerTask, \
    ManufacturerCodeMappingTransformerTask, \
    LabTransformerTask, \
    LabCodeMappingTransformerTask
    # ReleaseCodeMappingTransformerTask,
from   datalabs.etl.orm.load import ORMLoaderTask
from   datalabs.etl.parse.transform import ParseToCSVTransformerTask
from   datalabs.etl.s3.extract import S3FileExtractorTask


@register(name="CPTAPI")
class CPTAPIDAG(DAG):
    UNZIP_DISTRIBUTION: UnzipTransformerTask
    EXTRACT_DISTRIBUTION_RELEASES: S3FileExtractorTask
    CREATE_PDFS_ZIP: ZipTransformerTask
    CREATE_RELEASE_TYPES: ReleaseTypesTransformerTask
    LOAD_RELEASE_TYPES: ORMLoaderTask
    PARSE_TEXT_FILES: ParseToCSVTransformerTask
    CREATE_CODE_TABLE: CodesTransformerTask
    # CREATE_RELEASE_CODE_MAPPING_TABLE: ReleaseCodeMappingTransformerTask
    CREATE_SHORT_DESCRIPTOR_TABLE: ShortDescriptorTransformerTask
    CREATE_MEDIUM_DESCRIPTOR_TABLE: MediumDescriptorTransformerTask
    CREATE_LONG_DESCRIPTOR_TABLE: LongDescriptorTransformerTask
    CREATE_MODIFIER_TYPE_TABLE: ModifierTypeTransformerTask
    CREATE_MODIFIER_TABLE: ModifierTransformerTask
    CREATE_CONSUMER_DESCRIPTOR_TABLE: ConsumerDescriptorTransformerTask
    CREATE_CLINICIAN_DESCRIPTOR_TABLE: ClinicianDescriptorTransformerTask
    CREATE_CLINICIAN_DESCRIPTOR_CODE_MAPPING_TABLE: ClinicianDescriptorCodeMappingTransformerTask
    CREATE_PLA_DETAILS_TABLE: PLADetailsTransformerTask
    CREATE_MANUFACTURER_TABLE: ManufacturerTransformerTask
    CREATE_MANUFACTURER_CODE_MAPPING_TABLE: ManufacturerCodeMappingTransformerTask
    CREATE_LAB_TABLE: LabTransformerTask
    CREATE_LAB_CODE_MAPPING_TABLE: LabCodeMappingTransformerTask
    LOAD_RELEASE_TABLE: ORMLoaderTask
    LOAD_CODE_TABLE: ORMLoaderTask
    # LOAD_RELEASE_CODE_MAPPING_TABLE: ORMLoaderTask
    LOAD_MODIFIER_TYPE_TABLE: ORMLoaderTask
    LOAD_CLINICIAN_DESCRIPTOR_TABLE: ORMLoaderTask
    LOAD_DESCRIPTOR_TABLES: ORMLoaderTask
    LOAD_MANUFACTURER_TABLE: ORMLoaderTask
    LOAD_LAB_TABLE: ORMLoaderTask
    LOAD_PLA_DETAILS_TABLE: ORMLoaderTask
    LOAD_PLA_MAPPING_TABLES: ORMLoaderTask


# pylint: disable=pointless-statement
CPTAPIDAG.UNZIP_DISTRIBUTION >> CPTAPIDAG.PARSE_TEXT_FILES
CPTAPIDAG.UNZIP_DISTRIBUTION >> CPTAPIDAG.CREATE_PDFS_ZIP

# CPTAPIDAG.PARSE_TEXT_FILES >> CPTAPIDAG.CREATE_RELEASE_TABLE
CPTAPIDAG.PARSE_TEXT_FILES >> CPTAPIDAG.CREATE_CODE_TABLE
# CPTAPIDAG.PARSE_TEXT_FILES >> CPTAPIDAG.CREATE_RELEASE_CODE_MAPPING_TABLE
CPTAPIDAG.PARSE_TEXT_FILES >> CPTAPIDAG.CREATE_SHORT_DESCRIPTOR_TABLE
CPTAPIDAG.PARSE_TEXT_FILES >> CPTAPIDAG.CREATE_MEDIUM_DESCRIPTOR_TABLE
CPTAPIDAG.PARSE_TEXT_FILES >> CPTAPIDAG.CREATE_LONG_DESCRIPTOR_TABLE
CPTAPIDAG.PARSE_TEXT_FILES >> CPTAPIDAG.CREATE_MODIFIER_TYPE_TABLE
CPTAPIDAG.PARSE_TEXT_FILES >> CPTAPIDAG.CREATE_MODIFIER_TABLE
CPTAPIDAG.PARSE_TEXT_FILES >> CPTAPIDAG.CREATE_CONSUMER_DESCRIPTOR_TABLE
CPTAPIDAG.PARSE_TEXT_FILES >> CPTAPIDAG.CREATE_CLINICIAN_DESCRIPTOR_TABLE
CPTAPIDAG.PARSE_TEXT_FILES >> CPTAPIDAG.CREATE_CLINICIAN_DESCRIPTOR_CODE_MAPPING_TABLE
CPTAPIDAG.PARSE_TEXT_FILES >> CPTAPIDAG.CREATE_PLA_DETAILS_TABLE
CPTAPIDAG.PARSE_TEXT_FILES >> CPTAPIDAG.CREATE_MANUFACTURER_TABLE
CPTAPIDAG.PARSE_TEXT_FILES >> CPTAPIDAG.CREATE_MANUFACTURER_CODE_MAPPING_TABLE
CPTAPIDAG.PARSE_TEXT_FILES >> CPTAPIDAG.CREATE_LAB_TABLE
CPTAPIDAG.PARSE_TEXT_FILES >> CPTAPIDAG.CREATE_LAB_CODE_MAPPING_TABLE

CPTAPIDAG.CREATE_RELEASE_TYPES >> CPTAPIDAG.LOAD_RELEASE_TYPES

# CPTAPIDAG.CREATE_RELEASE_TYPES >> CPTAPIDAG.CREATE_RELEASE_TABLE

# CPTAPIDAG.CREATE_CODE_TABLE >> CPTAPIDAG.CREATE_RELEASE_CODE_MAPPING_TABLE
# CPTAPIDAG.CREATE_RELEASE_TABLE >> CPTAPIDAG.CREATE_RELEASE_CODE_MAPPING_TABLE

CPTAPIDAG.CREATE_CODE_TABLE >> CPTAPIDAG.CREATE_SHORT_DESCRIPTOR_TABLE
CPTAPIDAG.CREATE_CODE_TABLE >> CPTAPIDAG.CREATE_MEDIUM_DESCRIPTOR_TABLE
CPTAPIDAG.CREATE_CODE_TABLE >> CPTAPIDAG.CREATE_LONG_DESCRIPTOR_TABLE
CPTAPIDAG.CREATE_CODE_TABLE >> CPTAPIDAG.CREATE_CONSUMER_DESCRIPTOR_TABLE
CPTAPIDAG.CREATE_CODE_TABLE >> CPTAPIDAG.CREATE_CLINICIAN_DESCRIPTOR_CODE_MAPPING_TABLE
CPTAPIDAG.CREATE_CODE_TABLE >> CPTAPIDAG.LOAD_CODE_TABLE

# CPTAPIDAG.LOAD_RELEASE_TABLE >> CPTAPIDAG.LOAD_RELEASE_CODE_MAPPING_TABLE
# CPTAPIDAG.LOAD_CODE_TABLE >> CPTAPIDAG.LOAD_RELEASE_CODE_MAPPING_TABLE
# CPTAPIDAG.CREATE_RELEASE_CODE_MAPPING_TABLE >> CPTAPIDAG.LOAD_RELEASE_CODE_MAPPING_TABLE

CPTAPIDAG.CREATE_CLINICIAN_DESCRIPTOR_TABLE \
    >> CPTAPIDAG.LOAD_CLINICIAN_DESCRIPTOR_TABLE \
    >> CPTAPIDAG.LOAD_DESCRIPTOR_TABLES

CPTAPIDAG.CREATE_MODIFIER_TYPE_TABLE >> CPTAPIDAG.CREATE_MODIFIER_TABLE
CPTAPIDAG.CREATE_MODIFIER_TYPE_TABLE >> CPTAPIDAG.LOAD_MODIFIER_TYPE_TABLE

CPTAPIDAG.LOAD_MODIFIER_TYPE_TABLE >> CPTAPIDAG.LOAD_DESCRIPTOR_TABLES
CPTAPIDAG.CREATE_SHORT_DESCRIPTOR_TABLE >> CPTAPIDAG.LOAD_DESCRIPTOR_TABLES
CPTAPIDAG.CREATE_MEDIUM_DESCRIPTOR_TABLE >> CPTAPIDAG.LOAD_DESCRIPTOR_TABLES
CPTAPIDAG.CREATE_LONG_DESCRIPTOR_TABLE >> CPTAPIDAG.LOAD_DESCRIPTOR_TABLES
CPTAPIDAG.CREATE_CONSUMER_DESCRIPTOR_TABLE >> CPTAPIDAG.LOAD_DESCRIPTOR_TABLES
CPTAPIDAG.CREATE_CLINICIAN_DESCRIPTOR_CODE_MAPPING_TABLE >> CPTAPIDAG.LOAD_DESCRIPTOR_TABLES
CPTAPIDAG.CREATE_MODIFIER_TABLE >> CPTAPIDAG.LOAD_DESCRIPTOR_TABLES
CPTAPIDAG.LOAD_CODE_TABLE >> CPTAPIDAG.LOAD_DESCRIPTOR_TABLES

CPTAPIDAG.EXTRACT_DISTRIBUTION_RELEASES >> CPTAPIDAG.LOAD_RELEASE_TABLE
# CPTAPIDAG.CREATE_RELEASE_TABLE >> CPTAPIDAG.LOAD_RELEASE_TABLE
CPTAPIDAG.LOAD_RELEASE_TYPES >> CPTAPIDAG.LOAD_RELEASE_TABLE

CPTAPIDAG.CREATE_PLA_DETAILS_TABLE >> CPTAPIDAG.CREATE_MANUFACTURER_CODE_MAPPING_TABLE
CPTAPIDAG.CREATE_MANUFACTURER_TABLE >> CPTAPIDAG.CREATE_MANUFACTURER_CODE_MAPPING_TABLE

CPTAPIDAG.CREATE_PLA_DETAILS_TABLE >> CPTAPIDAG.CREATE_LAB_CODE_MAPPING_TABLE
CPTAPIDAG.CREATE_LAB_TABLE >> CPTAPIDAG.CREATE_LAB_CODE_MAPPING_TABLE

CPTAPIDAG.CREATE_LAB_TABLE >> CPTAPIDAG.LOAD_LAB_TABLE

CPTAPIDAG.CREATE_MANUFACTURER_TABLE >> CPTAPIDAG.LOAD_MANUFACTURER_TABLE

CPTAPIDAG.CREATE_PLA_DETAILS_TABLE >> CPTAPIDAG.LOAD_PLA_DETAILS_TABLE
CPTAPIDAG.CREATE_MANUFACTURER_TABLE >> CPTAPIDAG.LOAD_PLA_DETAILS_TABLE
CPTAPIDAG.CREATE_MANUFACTURER_CODE_MAPPING_TABLE >> CPTAPIDAG.LOAD_PLA_DETAILS_TABLE
CPTAPIDAG.CREATE_LAB_TABLE >> CPTAPIDAG.LOAD_PLA_DETAILS_TABLE
CPTAPIDAG.CREATE_LAB_CODE_MAPPING_TABLE >> CPTAPIDAG.LOAD_PLA_DETAILS_TABLE

CPTAPIDAG.LOAD_MANUFACTURER_TABLE >> CPTAPIDAG.LOAD_PLA_DETAILS_TABLE
CPTAPIDAG.LOAD_CODE_TABLE >> CPTAPIDAG.LOAD_PLA_DETAILS_TABLE

CPTAPIDAG.LOAD_PLA_DETAILS_TABLE >> CPTAPIDAG.LOAD_PLA_MAPPING_TABLES