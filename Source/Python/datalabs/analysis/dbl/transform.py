""" Transformer for DBL Report Creation """

from io import BytesIO, StringIO
import logging
import numpy as np
import pandas as pd
from string import ascii_uppercase
import xlsxwriter


from datalabs.etl.transform import TransformerTask

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


def format_column_as_percentage(data: pd.DataFrame, column_name: str):
    df = data.copy()
    df[column_name] *= 100
    return df


def get_letters_between(start, end):
    return ascii_uppercase[ascii_uppercase.index(start): ascii_uppercase.index(end)+1]


class DBLReportTransformer(TransformerTask):
    def _transform(self) -> 'Transformed Data':
        dataframes = self._get_dataframes(self._parameters['data'])
        dataframes[0] = self._transform_tab1(dataframes[0])
        dataframes[1] = self._transform_tab2(dataframes[1])
        dataframes[2] = self._transform_tab3(dataframes[2])
        dataframes[3] = self._transform_tab4(dataframes[3])
        dataframes[4] = self._transform_tab5(dataframes[4])
        dataframes[5] = self._transform_tab6(dataframes[5])
        dataframes[6] = self._transform_tab7(dataframes[6])
        dataframes[7] = self._transform_tab8(dataframes[7])
        dataframes[8] = self._transform_tab9(dataframes[8])
        dataframes[9] = self._transform_tab10(dataframes[9])

        output = self._make_excel_workbook(sheet_dataframes=dataframes)
        return [output.read()]

    @classmethod
    def _get_dataframes(cls, data):
        tab_1_data =  pd.read_csv(BytesIO(data[0]), delimiter='|', header=None)
        tab_2_data =  pd.read_csv(BytesIO(data[1]), delimiter='|')
        tab_3_data =  pd.read_csv(BytesIO(data[2]), delimiter='|')
        tab_4_data =  pd.read_csv(BytesIO(data[3]), delimiter='|')
        tab_5_data =  pd.read_csv(BytesIO(data[4]), delimiter='|')
        tab_6_data =  pd.read_csv(BytesIO(data[5]), delimiter='|', header=None)
        tab_7_data =  pd.read_csv(BytesIO(data[6]), delimiter='|', header=None)
        tab_8_data =  pd.read_csv(BytesIO(data[7]), delimiter='|', header=None)
        tab_9_data =  pd.read_csv(BytesIO(data[8]), delimiter='|', header=None)
        tab_10_data = pd.read_csv(BytesIO(data[9]), delimiter='|', header=None)
        return [
            tab_1_data,
            tab_2_data,
            tab_3_data,
            tab_4_data,
            tab_5_data,
            tab_6_data,
            tab_7_data,
            tab_8_data,
            tab_9_data,
            tab_10_data
        ]

    @classmethod
    def _transform_tab1(cls, data):
        """ ChangeFileAudit """
        return data.fillna('')

    @classmethod
    def _transform_tab2(cls, data):
        """ ReportByFieldFrom SAS """
        # no transformation required
        return format_column_as_percentage(data, column_name='PERCENTAGE').fillna('')

    @classmethod
    def _transform_tab3(cls, data):
        """ ChangeByFieldCount """
        return data.fillna('')

    @classmethod
    def _transform_tab4(cls, data):
        """ RecordActionExtract """
        # no transformation required
        return data

    @classmethod
    def _transform_tab5(cls, data):
        """ ChangeByRecordCount """
        return format_column_as_percentage(data, column_name='PERCENTAGE').fillna('')

    @classmethod
    def _transform_tab6(cls, data):
        """ PE Counts """

        data.columns = ['Total', 'PE Code', 'Description']
        data['PE Code'] = data['PE Code'].apply(lambda x: ('000' + str(x))[-3:])

        table = pd.pivot_table(
            data,
            values='Total',
            index=['PE Code', 'Description'],
            aggfunc=np.sum,
            fill_value=0,
            margins=True
        ).rename(index={'All': 'Grand Total'})

        return table

    @classmethod
    def _transform_tab7(cls, data):
        """ TOP Counts """

        data.columns = ['Total', 'TOP Code', 'Description']
        data['TOP Code'] = data['TOP Code'].apply(lambda x: ('000' + str(x))[-3:])

        table = pd.pivot_table(
            data,
            values='Total',
            index=['TOP Code', 'Description'],
            aggfunc=np.sum,
            fill_value=0,
            margins=True
        ).rename(index={'All': 'Grand Total'})

        return table

    @classmethod
    def _transform_tab8(cls, data):
        """ TOP by PE """

        data.columns = ['TOP Code', 'Description', 'PE Code', 'Count']
        data['TOP Code'] = data['TOP Code'].apply(lambda x: ('000' + str(x))[-3:])
        data['PE Code'] = data['PE Code'].apply(lambda x: ('000' + str(x))[-3:])

        table = pd.pivot_table(
            data,
            values='Count',
            columns=['PE Code'],
            index=['TOP Code', 'Description'],
            aggfunc=np.sum,
            fill_value=0,
            margins=True
        ).rename(columns={'All': 'Grand Total'}).rename(index={'All': 'Grand Total'})

        return table

    @classmethod
    def _transform_tab9(cls, data):
        """ PrimSpecbyMPA """

        data.columns = ['SPEC Code', 'Description', 'MPA', 'Count']
        table = cls._make_spec_pivot_table(data)
        return table

    @classmethod
    def _transform_tab10(cls, data):
        """ SecSpecbyMPA """

        data.columns = ['SPEC Code', 'Description', 'MPA', 'Count']
        table = cls._make_spec_pivot_table(data)
        return table

    @classmethod
    def _make_spec_pivot_table(cls, data: pd.DataFrame):
        table = pd.pivot_table(
            data,
            values='Count',
            columns=['MPA'],
            index=['SPEC Code', 'Description'],
            aggfunc=np.sum,
            fill_value=0,
            margins=True
        ).rename(columns={'All': 'Grand Total'}).rename(index={'All': 'Grand Total'})
        return table

    @classmethod
    def _make_excel_workbook(cls, sheet_dataframes):
        output = BytesIO()
        writer = pd.ExcelWriter('temp.xlsx', engine='xlsxwriter')
        writer.book = xlsxwriter.Workbook(output, {'in_memory': True})

        sheet_dataframes[0].to_excel(writer, sheet_name='ChangeFileAudit', header=False, index=False)
        sheet_dataframes[1].to_excel(writer, sheet_name='ReportByFieldFrom SAS', index=False)
        sheet_dataframes[2].to_excel(writer, sheet_name='ChangeByFieldCount', index=False)
        sheet_dataframes[3].to_excel(writer, sheet_name='RecordActionExtract', index=False)
        sheet_dataframes[4].to_excel(writer, sheet_name='ChangeByRecordCount', index=False)
        sheet_dataframes[5].to_excel(writer, sheet_name='PE Counts')
        sheet_dataframes[6].to_excel(writer, sheet_name='TOP Counts')
        sheet_dataframes[7].to_excel(writer, sheet_name='TOP by PE')
        sheet_dataframes[8].to_excel(writer, sheet_name='PrimSpecbyMPA')
        sheet_dataframes[9].to_excel(writer, sheet_name='SecSpecbyMPA')

        cls._format_workbook(writer.book)
        writer.save()

        output.seek(0)

        return output

    @classmethod
    def _format_workbook(cls, workbook: xlsxwriter.workbook):
        cls._format_workbook_column_widths(workbook)
        cls._format_workbook_percentage_columns(workbook)

    @classmethod
    def _format_workbook_column_widths(cls, workbook: xlsxwriter.workbook):
        sheet_column_widths = {
            'ChangeFileAudit': {
                'A:A': 31
            },
            'ReportByFieldFrom SAS': {
                'A:A': 31,
                'B:B': 8,
                'C:C': 12
            },
            'ChangeByFieldCount': {
                'A:A': 37,
                'B:B': 9,
                'C:C': 14
            },
            'RecordActionExtract': {
                'A:A': 21,
                'B:B': 12
            },
            'ChangeByRecordCount': {
                'A:A': 21,
                'C:C': 12
            },
            'PE Counts': {
                'A:A': 12,
                'B:B': 50,
                'C:C': 8
            },
            'TOP Counts': {
                'A:A': 12,
                'B:B': 29,
                'C:C': 8
            },
            'TOP by PE': {
                'A:A': 13,
                'B:B': 29,
                'U:U': 12,
            },
            'PrimSpecbyMPA': {
                'A:A': 11,
                'B:B': 80,
                'N:N': 12
            },
            'SecSpecbyMPA': {
                'A:A': 11,
                'B:B': 80,
                'N:N': 12
            }
        }

        for col in get_letters_between('C', 'T'):  # 'C' through 'T' on sheet 'TOP by PE'
            colname = f'{col}:{col}'
            sheet_column_widths['TOP by PE'][colname] = 8

        for col in get_letters_between('C', 'M'):  # 'C' through 'M' on sheets 'PrimSpecbyMPA' and 'SecSpecbyMPA'
            colname = f'{col}:{col}'
            sheet_column_widths['PrimSpecbyMPA'][colname] = 8
            sheet_column_widths['SecSpecbyMPA'][colname] = 8

        for sheetname in sheet_column_widths:
            for column in sheet_column_widths[sheetname]:
                width = sheet_column_widths[sheetname][column]
                workbook.get_worksheet_by_name(sheetname).set_column(column, width)

    @classmethod
    def _format_workbook_percentage_columns(cls, workbook: xlsxwriter.workbook):
        sheet_percentage_columns = {
            'ReportByFieldFrom SAS': ['C:C'],
            'ChangeByRecordCount': ['C:C']
        }

        percentage_format = workbook.add_format({'num_format': '0.00%'})

        for sheet_name in sheet_percentage_columns:
            columns = sheet_percentage_columns[sheet_name]
            for column in columns:
                workbook.get_worksheet_by_name(sheet_name).set_column(column, 12, percentage_format)
