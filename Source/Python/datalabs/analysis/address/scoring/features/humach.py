""" Adds Humach-survey-based features a dataset utilizing the ENTITY_COMM_AT table from AIMS """
# pylint: disable=import-error, singleton-comparison
from datetime import datetime
from io import BytesIO, StringIO
import os
import warnings
import pandas as pd
from tqdm import tqdm
from datalabs.analysis.address.scoring.common import log_info, rename_columns_in_uppercase
from datalabs.etl.transform import TransformerTask


warnings.filterwarnings('ignore', '.*A value is trying to be set on a copy of a slice from a DataFrame.*')
warnings.filterwarnings('ignore', '.*SettingWithCopyWarning*')
warnings.filterwarnings('ignore', '.*FutureWarning*')


def prepare_latest_humach_data(humach_data: pd.DataFrame, as_of_date):
    log_info('PREPARING HUMACH DATA')
    rename_columns_in_uppercase(humach_data)
    humach_data = add_survey_date_col_to_humach_data(humach_data)
    humach_data['SURVEY_DATE'] = pd.to_datetime(humach_data['SURVEY_DATE'])
    humach_data = humach_data[humach_data['SURVEY_DATE'] <= datetime.strptime(as_of_date, '%Y-%m-%d')]

    if 'ADDRESS_KEY' not in humach_data.columns:
        humach_data['ADDRESS_KEY'] = humach_data['ADDRESS_LINE_1'].fillna('').apply(
            str.strip
        ).apply(str.upper) + '_' + humach_data['ZIP'].fillna('').apply(
            str.strip
        ).apply(str.upper)

    humach_data = humach_data[
        ['ENTITY_ID', 'ADDRESS_KEY', 'SURVEY_DATE', 'COMMENTS', 'OFFICE_ADDRESS_VERIFIED_UPDATED']
    ].sort_values(
        by='SURVEY_DATE'
    ).groupby(['ENTITY_ID', 'ADDRESS_KEY']).last().reset_index()
    humach_data = add_address_status_info(humach_data)
    return humach_data.drop_duplicates()


def add_humach_features(base_data: pd.DataFrame, humach_data: pd.DataFrame, as_of_date: str, save_dir=None):
    base_data.columns = [col.upper() for col in base_data.columns]
    humach_data = prepare_latest_humach_data(humach_data, as_of_date)

    data = humach_data[humach_data['ENTITY_ID'].isin(base_data['ENTITY_ID'].values)]

    data['HUMACH_YEARS_SINCE_SURVEY'] = datetime.strptime(as_of_date, '%Y-%m-%d') - data['SURVEY_DATE']
    data['HUMACH_YEARS_SINCE_SURVEY'] = data['HUMACH_YEARS_SINCE_SURVEY'].apply(lambda x: x.days / 365)
    max_time = max(data['HUMACH_YEARS_SINCE_SURVEY'].values)

    data['HUMACH_NEVER_SURVEYED'] = (data['HUMACH_YEARS_SINCE_SURVEY'].isna()).astype(int)
    data['HUMACH_YEARS_SINCE_SURVEY'].fillna(max_time)

    data = data[['ENTITY_ID', 'ADDRESS_KEY', 'HUMACH_YEARS_SINCE_SURVEY',
                 'HUMACH_NEVER_SURVEYED', 'HUMACH_ADDRESS_STATUS_UNKNOWN',
                 'HUMACH_ADDRESS_STATUS_CORRECT', 'HUMACH_ADDRESS_STATUS_INCORRECT']].drop_duplicates()

    if save_dir is not None:
        save_filename = os.path.join(save_dir, F'features__humach__{as_of_date}.txt')
        log_info(f'SAVING ENTITY_COMM FEATURES: {save_filename}')
        data.to_csv(save_filename, sep='|', index=False)
    return data


def add_survey_date_col_to_humach_data(humach_data: pd.DataFrame):
    if 'SURVEY_DATE' not in humach_data.columns:
        year_month_data = humach_data[['SURVEY_YEAR', 'SURVEY_MONTH']].drop_duplicates()
        year_month_data_dates = []
        for _, row in year_month_data.iterrows():
            date = datetime(year=row['SURVEY_YEAR'], month=row['SURVEY_MONTH'], day=1)
            year_month_data_dates.append(date)
        year_month_data['SURVEY_DATE'] = year_month_data_dates
        humach_data = humach_data.merge(year_month_data, on=['SURVEY_YEAR', 'SURVEY_MONTH'])
    return humach_data


def add_address_status_info(humach_data: pd.DataFrame):
    log_info('RESOLVING HUMACH RESULT ADDRESS STATUS')
    results = []
    for comment, update in tqdm(
        zip(
            humach_data['COMMENTS'].values,
            humach_data['OFFICE_ADDRESS_VERIFIED_UPDATED'].values
        ),
        total=humach_data.shape[0]
    ):
        results.append(get_address_status(comment, update))
    humach_data['ADDRESS_STATUS'] = results

    # dummies
    for status in ['UNKNOWN', 'CORRECT', 'INCORRECT']:
        col = f'HUMACH_ADDRESS_STATUS_{status}'
        humach_data[col] = humach_data['ADDRESS_STATUS'] == status
        humach_data[col] = humach_data[col].astype(int)
    del humach_data['ADDRESS_STATUS']
    return humach_data


def get_address_status(comment, verified_updated):
    """
    comment value is primarily a result of the PHONE call, but combined with the address_verified_updated flag we can
    determine what the result was for the address
    """
    status = 'UNKNOWN'
    if str(verified_updated).strip() == '2':
        status = 'INCORRECT'
    comments_unknown = ['2ND ATTEMPT', 'LANGUAGE/HEARING', 'DO NOT CALL', 'ANSWERING SERVICE',
                        'DECEASED', 'FAX MODEM', 'REFUSAL', 'RETIRED', 'WRONG NUMBER']
    if comment in comments_unknown:
        status = 'UNKNOWN'
    elif comment in ['COMPLETE', 'RESPONDED TO SURVEY - AMA'] and str(verified_updated) == '1':
        return 'CORRECT'
    return status


class HumachFeatureGenerationTransformerTask(TransformerTask):
    def _transform(self) -> 'Transformed Data':
        base_data = pd.read_csv(StringIO(self._parameters['data'][0].decode()), sep='|', dtype=str)
        humach_data = pd.read_csv(StringIO(self._parameters['data'][1].decode()), sep='|', dtype=str)
        as_of_date = self._parameters['as_of_date']

        features = add_humach_features(base_data, humach_data, as_of_date)
        result = BytesIO()
        features.to_csv(result, sep='|', index=False)
        result.seek(0)

        return [result.getvalue()]
