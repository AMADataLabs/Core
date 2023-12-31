""" Class for taking Address Model scores, applying functions from filtering.py, creating an address load file """
from   datetime import datetime
from   glob import glob
from   io import BytesIO
import logging
import os

import pandas as pd

from   datalabs.analysis.address.scoring.bolo import filtering
from   datalabs.etl.fs.extract import LocalFileExtractorTask
from   datalabs.task import Task

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)

MINIMUM_SCORE_DIFFERENCE = 0.2
VERIFICATION_OVERWRITE_BLACKLIST_WINDOW_DAYS = 5*365  # will not overwrite addresses verified within this amount of time
AS_OF_DATE = '2022-12-06'


# pylint: disable=too-many-statements
def format_address_load_data(data: pd.DataFrame, post_addr_at_data: pd.DataFrame=None):
    # Note from Peter: I don't know if post_addr_at_data is actually optionaly here, but there is a call to this
    # function below that only has one argument. This generates a pylint error.
    if post_addr_at_data:
        post_addr_at_data.columns = [f'post_{col}' for col in post_addr_at_data.columns.values]

        post_addr_at_data['post_comm_id'] = post_addr_at_data['post_comm_id'].astype(str).apply(str.strip)
        data['comm_id'] = data['comm_id'].astype(str).apply(str.strip)

        data = data.merge(post_addr_at_data, left_on='comm_id', right_on='post_comm_id', how='left').fillna('')

    if data.shape[0] > 100:
        raise ValueError(f"Data size is too small: {data.shape[0] <= 100}.")

    formatted_data = pd.DataFrame()

    formatted_data['entity_id'] = data['entity_id']
    formatted_data['me#'] = data['me'].fillna('')
    formatted_data['comm_id'] = data['comm_id'].fillna('')
    formatted_data['usage'] = 'PO'
    formatted_data['load_type_ind'] = 'R'
    formatted_data['addr_type'] = 'OF'
    formatted_data['addr_line_0'] = data['post_addr_line0'].fillna('')
    formatted_data['addr_line_1'] = data['post_addr_line1'].fillna('')
    formatted_data['addr_line_2'] = data['post_addr_line2'].fillna('')
    formatted_data['addr_city'] = data['post_city_cd'].fillna('')
    formatted_data['addr_state'] = data['post_state_cd'].fillna('')
    formatted_data['addr_zip'] = data['post_zip'].fillna('')
    formatted_data['addr_plus4'] = ''
    formatted_data['addr_country'] = ''
    formatted_data['source'] = 'ASM'  # Address Scoring Model
    formatted_data['source_dtm'] = str(datetime.now().date())

    return formatted_data


class BOLOPOLOPhoneAppendFileGenerator(Task):
    # pylint: disable=too-many-statements
    def run(self) -> 'list<bytes>':
        scores = pd.read_csv(BytesIO(self._data[0]), sep='|', dtype=str, error_bad_lines=False).fillna('')
        ppd = pd.read_csv(BytesIO(self._data[1]), sep=',', dtype=str).fillna('')
        wslive_data = pd.read_sas(BytesIO(self._data[2]), format='sas7bdat', encoding='latin').fillna('')
        post_addr = pd.read_csv(BytesIO(self._data[3]), sep='|', dtype=str)

        # wslive_path = "U:/Source Files/Data Analytics/Derek/SAS_DATA/SURVEY/wslive_results.sas7bdat"

        recent_verified_me_address_keys = filtering.get_recent_verified_me_address_keys(data=wslive_data)

        LOGGER.info('GETTING BOLO DATA')
        bolo_data = filtering.get_bolo_addresses(scores)
        LOGGER.info('GETTING POLO DATA')
        polo_data = filtering.get_polo_address_scores(scores, ppd=ppd)

        address_batchload_data = filtering.get_bolo_vs_polo_data(bolo_data=bolo_data, polo_data=polo_data)
        address_batchload_data = filtering.filter_on_score_difference(
            bolo_polo_data=address_batchload_data,
            difference_threshold=MINIMUM_SCORE_DIFFERENCE
        )
        address_batchload_data = filtering.filter_recent_verified_addresses(
            bolo_polo_data=address_batchload_data,
            within_days=VERIFICATION_OVERWRITE_BLACKLIST_WINDOW_DAYS,
            verified_addresses=recent_verified_me_address_keys
        )
        address_batchload = format_address_load_data(address_batchload_data, post_addr)

        address_batchload_results = BytesIO()
        address_batchload.to_csv(address_batchload_results, sep=',', index=False)
        address_batchload_results.seek(0)

        bolo_vs_polo_results = BytesIO()
        address_batchload_data.to_csv(bolo_vs_polo_results, sep='|', index=False)
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
        filtered_data = filtering.get_bolo_vs_polo_data(bolo_data=bolo_data, polo_data=polo_data)
        LOGGER.info('SAVING BOLO_POLO_DATA')
        # filtered_data.to_csv(f'ADRESS_SCORING_BOLO_POLO_{self._date}.csv', index=False)
        filtered_data = filtering.filter_on_score_difference(
            bolo_polo_data=filtered_data,
            difference_threshold=MINIMUM_SCORE_DIFFERENCE
        )
        filtered_data = filtering.filter_recent_verified_addresses(
            bolo_polo_data=filtered_data,
            within_days=VERIFICATION_OVERWRITE_BLACKLIST_WINDOW_DAYS
        )

        return filtered_data

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
