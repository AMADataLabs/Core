# Kari Palmier    9/9/19    Created
# Garrett Lappe   2022-11-12 - Edited
#############################################################################
import datetime
import warnings

import settings
from get_ods_db_tables import get_iqvia_all_phys_info
from datalabs.access.ods import ODS


warnings.filterwarnings("ignore")

init_save_dir = 'U:\\Source Files\\Data Analytics\\Data-Science\\Data\\IQVIA\\'

out_dir = init_save_dir
out_dir = out_dir.replace("/", "\\")
out_dir += "\\"

current_time = datetime.datetime.now()
start_time_str = current_time.strftime("%Y-%m-%d")

ods = ODS(
    parameters={
        'username': 'vigrose',
        'password': 'Ravenclaw10946!',
        'name': 'ODS'  # Your ODBC registered source name for ODS
    }
)

ods.connect()

iqvia_df = get_iqvia_all_phys_info(ods._connection)

ods.close()

out_file = out_dir + start_time_str + '_IQVIA_Data.csv'
iqvia_df.to_csv(out_file, index=False, header=True)
