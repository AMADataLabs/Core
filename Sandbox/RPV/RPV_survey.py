# Garrett Lappe -   September 2019
# garrett.lappe@ama-assn.org

"""
This script is a minimal module intended to run phone samples from Kari's Phone Disconnect Model
through RPV.

The bulk of the coding for the RPV API is in "RPV_Turbo.py"

All that's required here is Kari's sampling and importing the

"""

import pandas as pd

from RPV_Turbo import process_batch


""" This insert allows for the import below """
sys.path.insert(0, 'U:\\Source Files\\Data Analytics\\Data-Science\\Code-Library\\Common_Model_Code\\')
from create_model_sample import get_phone_sample  # Kari's sample selection function

sys.path.insert(0, 'U:\\Source Files\\Data Analytics\\Data-Science\\Code-Library\\Common_Code\\')
from LoggingModule import *
set_log_file('rpv.log', format_string='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


if __name__ == '__main__':

    # read scored PPD DPC pop
    model_pred_df = pd.read_csv(
        'U:\\Source Files\\Data Analytics\\Data-Science\\Data\\Phone_Disconnect_Model'
        '\\Phone_Disconnect_Scored_PPD_DPC_Pop.csv',
        delimiter=",",
        index_col=0,
        header=0,
        dtype=object)

    sample_df, uniq_pred_df = get_phone_sample(model_pred_df,
                                               [0.5],
                                               [1.0],
                                               [10000],
                                               'pred_probability',
                                               'ppd_telephone_number', 2)

    sample_phones_df = sample_df[['ppd_me_pad', 'ppd_telephone_number']]

    # TESTING PURPOSES, USING ONLY FIRST 2 RECORDS
    # sample_phones_df = sample_phones_df[:2]
    ##############################################

    process_batch(sample_phones_df, False)  # tests and archives RPV results, DOES NOT MAKE BATCH FILE
    logging.info('process_batch method is complete.')
