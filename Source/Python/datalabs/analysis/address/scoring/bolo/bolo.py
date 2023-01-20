""" Class for taking Address Model scores, applying functions from filtering.py, creating an address load file """
from datetime import datetime
from glob import glob
from io import BytesIO
import logging
import os
import pickle as pk

import pandas as pd

from datalabs.analysis.address.scoring.bolo import filtering
from datalabs.etl.fs.extract import LocalFileExtractorTask
from datalabs.etl.task import Task

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)

MINIMUM_SCORE_DIFFERENCE = 0.2
VERIFICATION_OVERWRITE_BLACKLIST_WINDOW_DAYS = 5*365  # will not overwrite addresses verified within this amount of time


def format_address_load_data(data: pd.DataFrame, post_addr_at_data: pd.DataFrame):
    post_addr_at_data.columns = [f'post_{col}' for col in post_addr_at_data.columns.values]

    post_addr_at_data['post_comm_id'] = post_addr_at_data['post_comm_id'].astype(str).apply(str.strip)
    data['comm_id'] = data['comm_id'].astype(str).apply(str.strip)

    data = data.merge(post_addr_at_data, left_on='comm_id', right_on='post_comm_id', how='left').fillna('')
    assert data.shape[0] > 100

    df = pd.DataFrame()

    df['entity_id'] = data['entity_id']
    df['me#'] = data['me'].fillna('')
    df['comm_id'] = data['comm_id'].fillna('')
    df['usage'] = 'PO'
    df['load_type_ind'] = 'R'
    df['addr_type'] = 'OF'
    df['addr_line_0'] = data['post_addr_line0'].fillna('')
    df['addr_line_1'] = data['post_addr_line1'].fillna('')
    df['addr_line_2'] = data['post_addr_line2'].fillna('')
    df['addr_city'] = data['post_city_cd'].fillna('')
    df['addr_state'] = data['post_state_cd'].fillna('')
    df['addr_zip'] = data['post_zip'].fillna('')
    df['addr_plus4'] = ''
    df['addr_country'] = ''
    df['source'] = 'ASM'  # Address Scoring Model
    df['source_dtm'] = str(datetime.now().date())

    return df


class BOLOPOLOPhoneAppendFileGenerator(TransformerTask):
    def _transform(self) -> 'Transformed Data':
        scores = pd.read_csv(BytesIO(self._parameters['data'][0]), sep='|', dtype=str, error_bad_lines=False).fillna('')
        ppd = pd.read_csv(BytesIO(self._parameters['data'][1]), sep=',', dtype=str).fillna('')
        wslive_data = pd.read_sas(BytesIO(self._parameters['data'][2]), format='sas7bdat', encoding='latin').fillna('')
        post_addr = pd.read_csv(BytesIO(self._parameters['data'][3]), sep='|', dtype=str)

        # wslive_path = "U:/Source Files/Data Analytics/Derek/SAS_DATA/SURVEY/wslive_results.sas7bdat"

        recent_verified_me_address_keys = filtering.get_recent_verified_me_address_keys(data=wslive_data)

        LOGGER.info('GETTING BOLO DATA')
        bolo_data = filtering.get_bolo_addresses(scores)
        LOGGER.info('GETTING POLO DATA')
        polo_data = filtering.get_polo_address_scores(scores, ppd=ppd)

        df = filtering.get_bolo_vs_polo_data(bolo_data=bolo_data, polo_data=polo_data)
        df = filtering.filter_on_score_difference(
            bolo_polo_data=df,
            difference_threshold=MINIMUM_SCORE_DIFFERENCE
        )
        df = filtering.filter_recent_verified_addresses(
            bolo_polo_data=df,
            within_days=VERIFICATION_OVERWRITE_BLACKLIST_WINDOW_DAYS,
            verified_addresses=recent_verified_me_address_keys
        )
        address_batchload = format_address_load_data(df, post_addr)

        address_batchload_results = BytesIO()
        address_batchload.to_csv(address_batchload_results, sep=',', index=False)
        address_batchload_results.seek(0)

        bolo_vs_polo_results = BytesIO()
        df.to_csv(bolo_vs_polo_results, sep='|', index=False)
        bolo_vs_polo_results.seek(0)

        return [bolo_vs_polo_results.getvalue(), address_batchload_results.getvalue()]



# pylint: disable=invalid-name, logging-fstring-interpolation
class BOLOAddressLoadFileGenerator:
    """
    If running automatically, you should specify environment variable ADDRESS_MODEL_OUTPUT_DIR which assumes
    that address scoring model output files are saved in the following naming convention:

    ADDRESS_SCORING_yyyy-mm-dd.csv

    """
    def __init__(self, scored_data: pd.DataFrame=None):
        model_output_dir = os.environ.get('ADDRESS_MODEL_OUTPUT_DIR')
        load_dir = os.environ.get("ADDRESS_MODEL_ADDRESS_LOAD_DIR")
        self._model_output_dir = model_output_dir + '/' if model_output_dir is not None else ''
        self._load_dir = load_dir + '/' if load_dir is not None else ''
        self._data = scored_data
        self._date = str(datetime.now().date())

        if self._load_dir is None:
            self._load_dir = ''

        if self._model_output_dir is None:
            self._model_output_dir = ''

        self.save_path = self._load_dir + f"BOLO_Address_{self._date}.txt"

        if self._data is None:
            # required if loading data automatically
            # self._model_output_dir = os.environ.get('ADDRESS_MODEL_OUTPUT_DIR')
            self._data = self._get_latest_address_scoring_output()

    def run(self):
        LOGGER.info("LOADING FILTERED ADDRESS DATA")
        filtered_bolo_vs_polo_data = self._get_filtered_data()
        LOGGER.info('FORMATTING ADDRESS LOAD FILE DATA')
        address_load_data = format_address_load_data(filtered_bolo_vs_polo_data)

        address_load_data.rename(
            columns={
                'me': 'me#',
                'addr_line0': 'addr_line_1',
                'addr_line1': 'addr_line_3',
                'addr_line2': 'addr_line_2',
                'city_cd': 'addr_city',
                'state_cd': 'addr_state',
                'zip': 'addr_zip'
            },
            inplace=True
        )

        ### if not is_valid_component_file_structure(data):
        ###     raise ValueError('ADDRESS LOAD FILE DOES NOT CONFORM TO REQUIRED FORMAT. SEE LOGGING ABOVE.')
        self._save(address_load_data)
        LOGGER.info("COMPLETE")

    def _get_latest_address_scoring_output(self):
        files = glob(self._model_output_dir + 'ADDRESS_SCORING_*.csv')
        for file in files:
            LOGGER.info(f'FOUND SCORING FILE {file}')
        latest = sorted(files, reverse=True)[0]
        LOGGER.info(f'USING ADDRESS SCORING FILE: {latest}')
        return pd.read_csv(latest, dtype=str)

    def _get_filtered_data(self):
        LOGGER.info('GETTING BOLO DATA')
        bolo_data = filtering.get_bolo_addresses(self._data)
        LOGGER.info('GETTING POLO DATA')
        polo_data = filtering.get_polo_address_scores(self._data)
        df = filtering.get_bolo_vs_polo_data(bolo_data=bolo_data, polo_data=polo_data)
        LOGGER.info('SAVING BOLO_POLO_DATA')
        # df.to_csv(f'ADRESS_SCORING_BOLO_POLO_{self._date}.csv', index=False)
        df = filtering.filter_on_score_difference(
            bolo_polo_data=df,
            difference_threshold=MINIMUM_SCORE_DIFFERENCE
        )
        df = filtering.filter_recent_verified_addresses(
            bolo_polo_data=df,
            within_days=VERIFICATION_OVERWRITE_BLACKLIST_WINDOW_DAYS
        )

        return df

    def _save(self, data):
        LOGGER.info(f"SAVING ADDRESS LOAD FILE TO {self.save_path}")
        data.to_csv(self.save_path, sep='|', index=False)


if __name__ == '__main__':
    #gen = BOLOAddressLoadFileGenerator()
    #gen.run()
    ep = {
        'base_path': rf'C:\Users\Garrett\PycharmProjects\AMA'
                     rf'\hs-datalabs\Source\Python\datalabs\analysis\address\scoring\data\{AS_OF_DATE}',
        'files': rf'output\scores_{AS_OF_DATE}.txt,ppd_analysis_file.csv,wslive_results.sas7bdat'
    }
    e = LocalFileExtractorTask(parameters=ep)
    e.run()

    tp = {
        'data': e.data
    }
    t = BOLOPOLOPhoneAppendFileGenerator(parameters=tp)

    t.run()


    print(len(t.data))
