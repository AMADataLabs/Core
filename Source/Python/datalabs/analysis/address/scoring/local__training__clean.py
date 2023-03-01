""" Subsection of tasks specific to cleaning / preparation of data. Run this once on latest input sources. """


from datalabs.analysis.address.scoring.etl.transform.address_key import AddressKeyTransformerTask
from datalabs.analysis.address.scoring.etl.transform.cleanup import DatabaseTableCleanupTransformerTask
from datalabs.etl.fs.extract import LocalFileExtractorTask
from datalabs.etl.fs.load import LocalFileLoaderTask


AS_OF_DATE = '2022-12-06'

# Cleaning - License

extractor = LocalFileExtractorTask(
    {
        'base_path': 'data/{AS_OF_DATE}',
        'files': 'license_lt.csv'
    }
)
extractor_output = extractor.run()

transformer = DatabaseTableCleanupTransformerTask(
    {
        'clean_whitespace': 'TRUE',
        'date_columns': 'lic_issue_dt,lic_exp_dt',
        'repair_datetime': 'TRUE',
        'convert_to_int_columns': 'entity_id,comm_id'
    },
    extractor_output

)
transformer_output = transformer.run()

load = LocalFileLoaderTask(
    {
        'base_path': f'data/{AS_OF_DATE}',
        'files': 'license_lt_clean.txt'
    },
    transformer_output
)
load.run()


# Cleaning - post_addr

extractor = LocalFileExtractorTask(
    {
        'base_path': f'data/{AS_OF_DATE}',
        'files': 'post_addr.csv'
    }
)
extractor_output = extractor.run()

transformer = DatabaseTableCleanupTransformerTask(
    {
        'clean_whitespace': 'TRUE',
        'repair_datetime': 'TRUE',
        'convert_to_int_columns': 'comm_id,zip'
    },
    extractor_output
)
transformer_output = transformer.run()

load = LocalFileLoaderTask(
    {
        'base_path': f'data/{AS_OF_DATE}',
        'files': 'post_addr_at_clean.txt'
    },
    transformer_output
)
load.run()



# Cleaning - entity_comm

extractor = LocalFileExtractorTask(
    {
        'base_path': f'data/{AS_OF_DATE}',
        'files': 'entity_comm.csv'
    }
)
extractor_output = extractor.run()

transformer = DatabaseTableCleanupTransformerTask(
    {
        'date_columns': 'begin_dt,end_dt',
        'clean_whitespace': 'TRUE',
        'convert_to_int_columns': 'entity_id,comm_id'
    },
    extractor_output
)
transformer_output = transformer.run()

load = LocalFileLoaderTask(
    {
        'base_path': f'data/{AS_OF_DATE}',
        'files': 'entity_comm_at_clean.txt'
    },
    transformer_output
)
load.run()


# Cleaning - entity_comm_usg

extractor = LocalFileExtractorTask(
    {
        'base_path': f'data/{AS_OF_DATE}',
        'files': 'entity_comm_usg.csv'
    }
)
extractor_output = extractor.run()

transformer = DatabaseTableCleanupTransformerTask(
    {
        'date_columns': 'usg_begin_dt,end_dt',
        'clean_whitespace': 'TRUE',
        'repair_datetime': 'TRUE',
        'convert_to_int_columns': 'entity_id,comm_id'
    },
    extractor_output
)
transformer_output = transformer.run()

load = LocalFileLoaderTask(
    {
        'base_path': f'data/{AS_OF_DATE}',
        'files': 'entity_comm_usg_at_clean.txt'
    },
    transformer_output
)
load.run()





# Triangulation - Symphony - create address key

extractor = LocalFileExtractorTask(
    {
        'base_path': f'data/{AS_OF_DATE}',
        'files': 'symphony.csv'
    }
)
extractor_output = extractor.run()

transformer = AddressKeyTransformerTask(
    {
        'street_address_column': 'sym_polo_mailing_line_2',
        'zip_column': 'sym_polo_zip',
        'keep_columns': ''
    },
    extractor_output
)
transformer_output = transformer.run()

load = LocalFileLoaderTask(
    {
        'base_path': f'data/{AS_OF_DATE}',
        'files': 'triangulation_symphony.txt'
    },
    transformer_output
)
load.run()


# Triangulation - IQVIA - create address key

extractor = LocalFileExtractorTask(
    {
        'base_path': f'data/{AS_OF_DATE}',
        'files': 'iqvia.csv'
    }
)
extractor_output = extractor.run()

transformer = AddressKeyTransformerTask(
    {
        'street_address_column': 'ims_polo_mailing_line_2',
        'zip_column': 'ims_polo_zip',
    },
    extractor_output
)
transformer_output = transformer.run()

load = LocalFileLoaderTask(
    {
        'base_path': f'data/{AS_OF_DATE}',
        'files': 'triangulation_iqvia.txt'
    },
    transformer_output
)
load.run()
