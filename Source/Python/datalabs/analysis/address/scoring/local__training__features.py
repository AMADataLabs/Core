""" Subsection of tasks specific to create features data """



from datalabs.analysis.address.scoring.etl.aggregator import FeatureAggregatorTransformerTask
from datalabs.analysis.address.scoring.features.entity_comm import EntityCommFeatureGenerationTransformerTask
from datalabs.analysis.address.scoring.features.entity_comm_usg import EntityCommUsgFeatureGenerationTransformerTask
from datalabs.analysis.address.scoring.features.license import LicenseFeatureGenerationTransformerTask
from datalabs.analysis.address.scoring.features.humach import HumachFeatureGenerationTransformerTask
from datalabs.analysis.address.scoring.features.triangulation import TriangulationFeatureTransformer

from datalabs.etl.fs.extract import LocalFileExtractorTask
from datalabs.etl.fs.load import LocalFileLoaderTask



TRAINING_FOLDER = '202208'  # the folder in which each grouped survey data is saved

DATA_DATE = '2022-12-06'  # the date of the input files -- current/latest snapshot -- NOT RELATED TO SURVEY DATE
# The following should exist:
#   datalabs/analysis/address/scoring/data/{DATA_DATA}/*   <- inside this folder are AIMS, ODS, and EDW tables, etc.


# list of survey dates -- referencing training datasets to process.
# Each should correspond to a .txt file inside TRAINING_FOLDER
DATES_TO_RUN = [
    '2021-12-01',
    '2022-01-01',
    '2022-02-01',
    '2022-03-01',
    '2022-04-01',
    '2022-05-01',
    '2022-06-01'
]


for AS_OF_DATE in DATES_TO_RUN:


    # The following file should exist for each run:
    #   datalabs/analysis/address/scoring/training/{TRAINING_FOLDER}/{AS_OF_DATE}.txt

    # License features

    from datalabs.analysis.address.scoring.features.license import LicenseFeatureGenerationTransformerTask
    extractor = LocalFileExtractorTask(
        parameters={
            'base_path': '',
            'files': f'training/{TRAINING_FOLDER}/{AS_OF_DATE}.txt,data/{DATA_DATE}/license_lt_clean.txt,data/{DATA_DATE}/post_addr_at_clean.txt',
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
            'base_path': f'training/{TRAINING_FOLDER}/features/',
            'files': f'features__license__{AS_OF_DATE}.txt'
        }
    )
    loader.run()



    # Humach features

    extractor = LocalFileExtractorTask(
        parameters={
            'base_path': '',
            'files': f'training/{TRAINING_FOLDER}/{AS_OF_DATE}.txt,data/{DATA_DATE}/wslive_results.sas7bdat'
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
            'base_path': f'training/{TRAINING_FOLDER}/features/',
            'files': f'features__humach__{AS_OF_DATE}.txt'
        }
    )
    loader.run()



    # Entity Comm features

    extractor = LocalFileExtractorTask(
        parameters={
            'base_path': '',
            'files': f'training/{TRAINING_FOLDER}/{AS_OF_DATE}.txt,data/{DATA_DATE}/entity_comm_at_clean.txt',
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
            'base_path': f'training/{TRAINING_FOLDER}/features/',
            'files': f'features__entity_comm__{AS_OF_DATE}.txt'
        }
    )
    loader.run()



    # Entity Comm Usg features

    extractor = LocalFileExtractorTask(
        parameters={
            'base_path': '',
            'files': f'training/{TRAINING_FOLDER}/{AS_OF_DATE}.txt,data/{DATA_DATE}/entity_comm_usg_at_clean.txt',
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
            'base_path': f'training/{TRAINING_FOLDER}/features/',
            'files': f'features__entity_comm_usg__{AS_OF_DATE}.txt'
        }
    )
    loader.run()



    # Triangulation features - IQVIA

    extractor = LocalFileExtractorTask(
        parameters={
            'base_path': '',
            'files': f'training/{TRAINING_FOLDER}/{AS_OF_DATE}.txt,data/{DATA_DATE}/triangulation_iqvia.txt',
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
            'base_path': f'training/{TRAINING_FOLDER}/features/',
            'files': f'features__triangulation__{TRIANGULATION_SOURCE}__{AS_OF_DATE}.txt'
        }
    )
    loader.run()



    # Triangulation features - Symphony

    TRIANGULATION_SOURCE = 'SYMPHONY'

    extractor = LocalFileExtractorTask(
        parameters={
            'base_path': '',
            'files': f'training/{TRAINING_FOLDER}/{AS_OF_DATE}.txt,data/{DATA_DATE}/triangulation_symphony.txt',
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
            'base_path': f'training/{TRAINING_FOLDER}/features/',
            'files': f'features__triangulation__{TRIANGULATION_SOURCE}__{AS_OF_DATE}.txt'
        }
    )
    loader.run()


    # AGGREGATOR  -- once all feature generation tasks are complete for this specific AS_OF_DATE, aggregate them

    extractor = LocalFileExtractorTask(
        parameters={
            #'base_path': 'data/2022-08-16/features/', # 'data/2020-06-24/features/' #
            'base_path': '',
            'files': f'training/{TRAINING_FOLDER}/{AS_OF_DATE}.txt,training/{TRAINING_FOLDER}/features/features__entity_comm__{AS_OF_DATE}.txt,training/{TRAINING_FOLDER}/features/features__entity_comm_usg__{AS_OF_DATE}.txt,training/{TRAINING_FOLDER}/features/features__license__{AS_OF_DATE}.txt,training/{TRAINING_FOLDER}/features/features__humach__{AS_OF_DATE}.txt,training/{TRAINING_FOLDER}/features/features__triangulation__IQVIA__{AS_OF_DATE}.txt,training/{TRAINING_FOLDER}/features/features__triangulation__SYMPHONY__{AS_OF_DATE}.txt'
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
            'base_path': f'training/{TRAINING_FOLDER}/features/',
            'files': f'aggregate_out__{AS_OF_DATE}.txt'
        }
    )
    loader.run()
