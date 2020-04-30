""" Apply the POLO address fitness model to the PPD. """
import logging
import os
from   pathlib import Path
import re

import settings  # pylint: disable=unused-import
import datalabs.analysis.polo.model as polo
import datalabs.analysis.polo.plot as plot
import datalabs.curate.polo.ppd as data

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


class POLOFitnessScoringApp:
    def run(self):
        model_input_files = self._get_input_files()
        scored_data_file = self._get_scored_data_file()
        archive_dir = os.environ.get('MODEL_ARCHIVE_DIR')
        expected_df_lengths = self._get_expected_df_lengths()

        input_data = data.InputDataLoader(expected_df_lengths).load(model_input_files)

        scored_data = polo.POLOFitnessModel(archive_dir).apply(input_data)

        self._save_scored_data(scored_data, scored_data_file)

        plot.scoring_statistics(scored_data)

    @classmethod
    def _get_expected_df_lengths(cls):
        return polo.ModelInputData(
            model=None,
            variables=None,
            ppd=1.3e6,
            entity=polo.EntityData(
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

        entity_files = polo.EntityData(
            entity_comm_at=os.environ.get('ENTITY_COMM_AT_FILE'),
            entity_comm_usg=os.environ.get('ENTITY_COMM_USG_FILE'),
            post_addr_at=os.environ.get('POST_ADDR_AT_FILE'),
            license_lt=os.environ.get('LICENSE_LT_FILE'),
            entity_key_et=os.environ.get('ENTITY_KEY_ET_FILE')
        )

        model = os.environ.get('MODEL_FILE')

        variables=polo.ModelVariables(
            input=set(os.environ.get('MODEL_INPUT_VARIABLES').split(',')),
            feature=None,
            output=set(os.environ.get('MODEL_OUTPUT_VARIABLES').split(',')),
        )

        return polo.ModelInputData(
            model=model,
            variables=variables,
            ppd=ppd_file,
            entity=entity_files,
            date=ppd_date

        )

    @classmethod
    def _get_scored_data_file(cls):
        return os.environ.get('MODEL_PREDICTIONS_FILE')

    @classmethod
    def _extract_ppd_date_from_filename(cls, ppd_file):
        """ Extract the timestamp from a PPD data file path of the form '.../ppd_data_YYYYMMDD.csv'. """
        ppd_filename = Path(ppd_file).name

        match = re.match(r'ppd_data_([0-9]+)\.csv', ppd_filename)

        return match.group(1)

    @classmethod
    def _save_scored_data(cls, scored_data, scored_data_file):
        LOGGER.info('Writing scored data to %s', scored_data_file)
        scored_data.to_csv(scored_data_file, index=False)
