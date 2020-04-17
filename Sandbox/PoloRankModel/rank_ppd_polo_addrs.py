'''
Run the POLO address rank scoring model using PPD and AIMS data.

Kari Palmier    7/31/19    Created
Kari Palmier    8/14/19    Updated to work with more generic get_sample
Peter Lane      3/17/2020  Refactored ranking code to datalabs.analysis.polo.fitness module
'''
import logging
import os
from   pathlib import Path
import re

import settings
from datalabs.analysis.polo.fitness import POLOFitnessModel, ModelInputData, ModelOutputData, ModelParameters, EntityData
import datalabs.curate.polo.ppd as data

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


class POLOFitnessScoringApp():
    def run(self):
        model_input_files = self._get_input_files()
        model_output_files = self._get_output_files()
        archive_dir = os.environ.get('MODEL_ARCHIVE_DIR')
        expected_df_lengths = self._get_expected_df_lengths()

        input_data = data.InputDataLoader(expected_df_lengths).load(model_input_files)

        model_output_data = POLOFitnessModel(archive_dir).apply(input_data)

        self._save_model_predictions(model_output_data, model_output_files)

    @classmethod
    def _get_expected_df_lengths(cls):
        return ModelInputData(
            model=None,
            ppd=1.3e6,
            entity=EntityData(
                entity_comm_at=33e6,
                entity_comm_usg=15e6,
                post_addr_at=16e6,
                license_lt=4e6,
                entity_key_et=14e6
            ),
            date=None
        )

    @classmethod
    def _get_input_files(cls):
        ppd_file = os.environ.get('PPD_FILE')
        ppd_date = cls._extract_ppd_date_from_filename(ppd_file)

        entity_files = EntityData(
            entity_comm_at=os.environ.get('ENTITY_COMM_AT_FILE'),
            entity_comm_usg=os.environ.get('ENTITY_COMM_USG_FILE'),
            post_addr_at=os.environ.get('POST_ADDR_AT_FILE'),
            license_lt=os.environ.get('LICENSE_LT_FILE'),
            entity_key_et=os.environ.get('ENTITY_KEY_ET_FILE')
        )

        model_parameters = ModelParameters(
            meta=os.environ.get('MODEL_FILE'),
            variables=os.environ.get('MODEL_VAR_FILE'),
        )

        return ModelInputData(
            model=model_parameters,
            ppd=ppd_file,
            entity=entity_files,
            date=ppd_date

        )

    @classmethod
    def _get_output_files(cls):
        return ModelOutputData(
            predictions=os.environ.get('MODEL_PREDICTIONS_FILE'),
            ranked_predictions=os.environ.get('MODEL_RANKED_PREDICTIONS_FILE')
        )

    @classmethod
    def _extract_ppd_date_from_filename(cls, ppd_file):
        """ Extract the timestamp from a PPD data file path of the form '.../ppd_data_YYYYMMDD.csv'. """
        ppd_filename = Path(ppd_file).name

        match = re.match(r'ppd_data_([0-9]+)\.csv', ppd_filename)

        return match.group(1)

    @classmethod
    def _save_model_predictions(cls, output_data, output_files):
        LOGGER.info('Writing model predictions to %s', output_files.predictions)
        output_data.predictions.to_csv(output_files.predictions, index=False)

        LOGGER.info('Writing scored model predictions to %s', output_files.ranked_predictions)
        output_data.ranked_predictions.to_csv(output_files.ranked_predictions, sep=',', header=True, index=True)


if __name__ == '__main__':
    POLOFitnessScoringApp().run()