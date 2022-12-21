"""
Address Scoring - Local execution

- specify AS_OF_DATE - example "2022-12-06"
- save required AIMS + ODS + EDW data to datalabs/analysis/address/scoring/data/2022-12-06
    - inside this folder, make the following folders: features, output
- run data cleaning tasks
- run PoloEligibleDataTransformerTask
- run feature engineering transformer tasks and feature aggregation task
- run AddressScoringTransformerTask to score the aggregated feature data
- run result processing transformer tasks (AddressScoreBatchFileTransformerTask, BOLOPOLOPhoneAppendFileGenerator)
"""
from datalabs.etl.fs.extract import LocalFileExtractorTask
from datalabs.etl.fs.load import LocalFileLoaderTask

from datalabs.analysis.address.scoring.etl.extract.basedata import PoloEligibleDataTransformerTask
from datalabs.analysis.address.scoring.etl.transform.address_key import AddressKeyTransformerTask
from datalabs.analysis.address.scoring.etl.transform.cleanup import DatabaseTableCleanupTransformerTask
from datalabs.analysis.address.scoring.etl.score import AddressScoringTransformerTask
from datalabs.analysis.address.scoring.etl.transform.batchload import AddressScoreBatchFileTransformerTask
from datalabs.analysis.address.scoring.etl.aggregator import FeatureAggregatorTransformerTask
from datalabs.analysis.address.scoring.features.entity_comm import EntityCommFeatureGenerationTransformerTask
from datalabs.analysis.address.scoring.features.entity_comm_usg import EntityCommUsgFeatureGenerationTransformerTask
from datalabs.analysis.address.scoring.features.license import LicenseFeatureGenerationTransformerTask
from datalabs.analysis.address.scoring.features.humach import HumachFeatureGenerationTransformerTask
from datalabs.analysis.address.scoring.features.triangulation import TriangulationFeatureTransformer
from datalabs.analysis.address.scoring.bolo.bolo import BOLOPOLOPhoneAppendFileGenerator


AS_OF_DATE = '2022-12-06'

# Cleaning - License

extractor = LocalFileExtractorTask(
    parameters={
        'base_path': f'data/{AS_OF_DATE}',
        'files': 'license_lt.csv'
    }
)
extractor.run()

transformer = DatabaseTableCleanupTransformerTask(
    parameters={
        'data': extractor.data,
        'clean_whitespace': 'TRUE',
        'date_columns': 'lic_issue_dt,lic_exp_dt',
        'repair_datetime': 'TRUE',
        'convert_to_int_columns': 'entity_id,comm_id'
    }
)
transformer.run()

load = LocalFileLoaderTask(
    parameters={
        'data': transformer.data,
        'base_path': f'data/{AS_OF_DATE}',
        'files': 'license_lt_clean.txt'
    }
)
load.run()


# Cleaning - post_addr

extractor = LocalFileExtractorTask(
    parameters={
        'base_path': f'data/{AS_OF_DATE}',
        'files': 'post_addr.csv'
    }
)
extractor.run()

transformer = DatabaseTableCleanupTransformerTask(
    parameters={
        'data': extractor.data,
        'clean_whitespace': 'TRUE',
        'repair_datetime': 'TRUE',
        'convert_to_int_columns': 'comm_id,zip'
    }
)
transformer.run()

load = LocalFileLoaderTask(
    parameters={
        'data': transformer.data,
        'base_path': f'data/{AS_OF_DATE}',
        'files': 'post_addr_at_clean.txt'
    }
)
load.run()



# Cleaning - entity_comm

extractor = LocalFileExtractorTask(
    parameters={
        'base_path': f'data/{AS_OF_DATE}',
        'files': 'entity_comm.csv'
    }
)
extractor.run()

transformer = DatabaseTableCleanupTransformerTask(
    parameters={
        'data': extractor.data,
        'date_columns': 'begin_dt,end_dt',
        'clean_whitespace': 'TRUE',
        'convert_to_int_columns': 'entity_id,comm_id'
    }
)
transformer.run()

load = LocalFileLoaderTask(
    parameters={
        'data': transformer.data,
        'base_path': f'data/{AS_OF_DATE}',
        'files': 'entity_comm_at_clean.txt'
    }
)
load.run()


# Cleaning - entity_comm_usg

extractor = LocalFileExtractorTask(
    parameters={
        'base_path': f'data/{AS_OF_DATE}',
        'files': 'entity_comm_usg.csv'
    }
)
extractor.run()

transformer = DatabaseTableCleanupTransformerTask(
    parameters={
        'data': extractor.data,
        'date_columns': 'usg_begin_dt,end_dt',
        'clean_whitespace': 'TRUE',
        'repair_datetime': 'TRUE',
        'convert_to_int_columns': 'entity_id,comm_id'
    }
)
transformer.run()

load = LocalFileLoaderTask(
    parameters={
        'data': transformer.data,
        'base_path': f'data/{AS_OF_DATE}',
        'files': 'entity_comm_usg_at_clean.txt'
    }
)
load.run()





# Triangulation - Symphony - create address key

extractor = LocalFileExtractorTask(
    parameters={
        'base_path': f'data/{AS_OF_DATE}',
        'files': 'symphony.csv'
    }
)
extractor.run()

transformer = AddressKeyTransformerTask(
    parameters={
        'data': extractor.data,
        'street_address_column': 'sym_polo_mailing_line_2',
        'zip_column': 'sym_polo_zip',
        'keep_columns': ''
    }
)
transformer.run()

load = LocalFileLoaderTask(
    parameters={
        'data': transformer.data,
        'base_path': f'data/{AS_OF_DATE}',
        'files': 'triangulation_symphony.txt'
    }
)
load.run()


# Triangulation - IQVIA - create address key

extractor = LocalFileExtractorTask(
    parameters={
        'base_path': f'data/{AS_OF_DATE}',
        'files': 'iqvia.csv'
    }
)
extractor.run()

transformer = AddressKeyTransformerTask(
    parameters={
        'data': extractor.data,
        'street_address_column': 'ims_polo_mailing_line_2',
        'zip_column': 'ims_polo_zip',
    }
)
transformer.run()

load = LocalFileLoaderTask(
    parameters={
        'data': transformer.data,
        'base_path': f'data/{AS_OF_DATE}',
        'files': 'triangulation_iqvia.txt'
    }
)
load.run()



# Base data - creation of DPC - polo-eligible address pair data

extractor = LocalFileExtractorTask(
    parameters={
        'base_path': f'data/{AS_OF_DATE}',
        'files': 'ppd_analysis_file.csv,entity_comm_at_clean.txt,post_addr_at_clean.txt',
    }
)
extractor.run()

transformer = PoloEligibleDataTransformerTask(
    parameters={
        'data': extractor.data,
        'as_of_date': AS_OF_DATE
    }
)
transformer.run()

loader = LocalFileLoaderTask(
    parameters={
        'data': transformer.data,
        'base_path': f'data/{AS_OF_DATE}/features',
        'files': f'base_data.txt'
    }
)
loader.run()



# License features

from datalabs.analysis.address.scoring.features.license import LicenseFeatureGenerationTransformerTask
extractor = LocalFileExtractorTask(
    parameters={
        'base_path': f'data/{AS_OF_DATE}',
        'files': 'features/base_data.txt,license_lt_clean.txt,post_addr_at_clean.txt',
}
)
extractor.run()

transformer = LicenseFeatureGenerationTransformerTask(
    parameters={
        'data': extractor.data,
        'as_of_date': AS_OF_DATE
    }
)
transformer.run()

loader = LocalFileLoaderTask(
    parameters={
        'data': transformer.data,
        'base_path': f'data/{AS_OF_DATE}/features/',
        'files': f'features__license__{AS_OF_DATE}.txt'
    }
)
loader.run()



# Humach features

extractor = LocalFileExtractorTask(
    parameters={
        'base_path': f'data/{AS_OF_DATE}',
        'files': 'features/base_data.txt,wslive_results.sas7bdat'
    }
)
extractor.run()

transformer = HumachFeatureGenerationTransformerTask(
    parameters={
        'data': extractor.data,
        'as_of_date': AS_OF_DATE
    }
)
transformer.run()

loader = LocalFileLoaderTask(
    parameters={
        'data': transformer.data,
        'base_path': f'data/{AS_OF_DATE}/features',
        'files': f'features__humach__{AS_OF_DATE}.txt'
    }
)
loader.run()



# Entity Comm features

extractor = LocalFileExtractorTask(
    parameters={
        'base_path': f'data/{AS_OF_DATE}',
        'files': 'features/base_data.txt,entity_comm_at_clean.txt',
    }
)
extractor.run()

transformer = EntityCommFeatureGenerationTransformerTask(
    parameters={
        'data': extractor.data,
        'as_of_date': AS_OF_DATE
    }
)
transformer.run()

loader = LocalFileLoaderTask(
    parameters={
        'data': transformer.data,
        'base_path': f'data/{AS_OF_DATE}/features',
        'files': f'features__entity_comm__{AS_OF_DATE}.txt'
    }
)
loader.run()



# Entity Comm Usg features

extractor = LocalFileExtractorTask(
    parameters={
        'base_path': f'data/{AS_OF_DATE}',
        'files': 'features/base_data.txt,entity_comm_usg_at_clean.txt',
    }
)
extractor.run()

transformer = EntityCommUsgFeatureGenerationTransformerTask(
    parameters={
        'data': extractor.data,
        'as_of_date': AS_OF_DATE
    }
)
transformer.run()

from datalabs.etl.fs.load import LocalFileLoaderTask

loader = LocalFileLoaderTask(
    parameters={
        'data': transformer.data,
        'base_path': f'data/{AS_OF_DATE}/features/',
        'files': f'features__entity_comm_usg__{AS_OF_DATE}.txt'
    }
)
loader.run()



# Triangulation features - IQVIA

extractor = LocalFileExtractorTask(
    parameters={
        'base_path': f'data/{AS_OF_DATE}',
        'files': 'features/base_data.txt,triangulation_iqvia.txt',
    }
)
extractor.run()

TRIANGULATION_SOURCE = 'IQVIA'

transformer = TriangulationFeatureTransformer(
    parameters={
        'data': extractor.data,
        'triangulation_source': TRIANGULATION_SOURCE,
        'as_of_date': AS_OF_DATE
    }
)
transformer.run()

loader = LocalFileLoaderTask(
    parameters={
        'data': transformer.data,
        'base_path': f'data/{AS_OF_DATE}/features',
        'files': f'features__triangulation__{TRIANGULATION_SOURCE}__{AS_OF_DATE}.txt'
    }
)
loader.run()



# Triangulation features - Symphony

TRIANGULATION_SOURCE = 'SYMPHONY'

extractor = LocalFileExtractorTask(
    parameters={
        'base_path': f'data/{AS_OF_DATE}',
        'files': 'features/base_data.txt,triangulation_symphony.txt',
    }
)
extractor.run()

transformer = TriangulationFeatureTransformer(
    parameters={
        'data': extractor.data,
        'triangulation_source': TRIANGULATION_SOURCE,
        'as_of_date': AS_OF_DATE
    }
)
transformer.run()

loader = LocalFileLoaderTask(
    parameters={
    'data': transformer.data,
    'base_path': f'data/{AS_OF_DATE}/features',
    'files': f'features__triangulation__{TRIANGULATION_SOURCE}__{AS_OF_DATE}.txt'
    }
)
loader.run()



# Feature aggregator

dates = [AS_OF_DATE]  # dates. In production application of latest snapshot, this is just 1 date. However, training data is created and saved according to its corresponding 'survey_date' so each date / folder will go here. Each "aggregate_out__{date}.txt" file will be concatenated and processed for model training.
for date in dates:
    extractor = LocalFileExtractorTask(
        parameters={
            #'base_path': 'data/2022-08-16/features/', # 'data/2020-06-24/features/' #
            'base_path': f'data/{AS_OF_DATE}',
            'files': f'features/base_data.txt, features/features__entity_comm__{date}.txt,features/features__entity_comm_usg__{date}.txt,features/features__license__{date}.txt,features/features__humach__{date}.txt,features/features__triangulation__IQVIA__{date}.txt,features/features__triangulation__SYMPHONY__{date}.txt'
        }
    )
    extractor.run()

    transformer = FeatureAggregatorTransformerTask(
        parameters={
            'data': extractor.data
        }
    )
    transformer.run()

    from datalabs.etl.fs.load import LocalFileLoaderTask
    loader = LocalFileLoaderTask(
        parameters={
            'data': transformer.data,
            'base_path': f'data/{AS_OF_DATE}/features/',
            'files': f'aggregate_out__{AS_OF_DATE}.txt'
        }
    )
    loader.run()




# Score

extractor = LocalFileExtractorTask(
    parameters={
        'base_path': '',
        'files': f'models/model_xgb_2022-09-15.pkl,data/{AS_OF_DATE}/features/aggregate_out__{AS_OF_DATE}.txt'
    }
)
extractor.run()

transformer = AddressScoringTransformerTask(parameters={'data': extractor.data})
transformer.run()

loader = LocalFileLoaderTask(
    parameters={
        'data': transformer.data,
        'base_path': f'data/{AS_OF_DATE}/output/',
        'files': f'scores.txt'
    }
)
loader.run()


# Score file batchload

extractor = LocalFileExtractorTask(
    parameters={
        'base_path': f'data/{AS_OF_DATE}',
        'files': f'output/scores_{AS_OF_DATE}.txt,party_key.txt,post_cd.txt'
    }
)
extractor.run()

transformer = AddressScoreBatchFileTransformerTask(
    parameters={
        'data': extractor.data,
    }
)
transformer.run()

loader = LocalFileLoaderTask(
    parameters={
        'data': transformer.data,
        'base_path': f'data/{AS_OF_DATE}/output/',
        'files': f'batchload_scores_{AS_OF_DATE}.txt'
    }
)
loader.run()


# BOLO vs POLO file - phone append file and replacement batchload file

extractor = LocalFileExtractorTask(
    parameters={
        'base_path': f'data/{AS_OF_DATE}',
        'files': f'output/scores_{AS_OF_DATE}.txt,ppd_analysis_file.csv,wslive_results.sas7bdat,post_addr_at_clean.txt'
    }
)
extractor.run()

transformer = BOLOPOLOPhoneAppendFileGenerator(
    parameters={
        'data': extractor.data
    }
)
transformer.run()

loader = LocalFileLoaderTask(
    parameters={
        'data': transformer.data,
        'base_path': f'data/{AS_OF_DATE}/output/',
        'files': f'BOLO_vs_POLO_{AS_OF_DATE}.txt,BOLO_batchload_{AS_OF_DATE}.txt'
    }
)
loader.run()

