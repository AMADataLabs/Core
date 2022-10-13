""" Transform Derek's WSLIVE_RESULTS SAS data """
# pylint: disable=import-error
import pickle as pk
from io import BytesIO, StringIO
import pandas as pd
from datalabs.etl.transform import TransformerTask


def get_sample_date(source_file_dt):
    day = int(source_file_dt[-2:])
    month = int(source_file_dt[5:7])
    year = int(source_file_dt[:4])

    if day >= 20:
        month = month + 1
        if month > 12:
            month = 1
            year = year + 1
    return f'{year}-{month}-01'


class WSLiveResultTransformerTask(TransformerTask):
    def _transform(self) -> 'Transformed Data':

        wslive_results = BytesIO()

        wslive_results.write(self._parameters['data'][0])
        wslive_results.seek(0)

        data = pd.read_sas(wslive_results, encoding='latin', format='sas7bdat')

        for col in data.columns.values:
            data[col] = data[col].fillna('').astype(str).apply(str.strip).apply(lambda x: ' '.join(x.split()))

        data['SOURCE_FILE_DT'] = pd.to_datetime(data['SOURCE_FILE_DT']).apply(lambda x: x.date()).astype(str)
        data['SOURCE_FILE_DT'].replace('NaT', '', inplace=True)

        last_seen_nn = ''
        for i, row in data.iterrows():
            source_file_dt = row['SOURCE_FILE_DT']
            if source_file_dt != '':
                last_seen_nn = source_file_dt
            else:
                data.loc[i, 'SOURCE_FILE_DT'] = last_seen_nn

        processed_data = pd.DataFrame()
        processed_data['me'] = data['PHYSICIAN_ME_NUMBER']
        processed_data['address_key'] = data['OFFICE_ADDRESS_LINE_2'].apply(str.upper) + '_' + data['OFFICE_ADDRESS_ZIP']
        processed_data['survey_data'] = data['SOURCE_FILE_DT'].apply(get_sample_date)
        processed_data['comments'] = data['COMMENTS']
        processed_data['office_address_verified_update'] = data['OFFICE_ADDRESS_VERIFIED_UPDATED']
        processed_data['party_id'] = ''
        processed_data['entity_id'] = ''

        output = StringIO()

        processed_data.to_csv(output, sep='|', index=False)
        output.seek(0)

        return [output.getvalue()]
