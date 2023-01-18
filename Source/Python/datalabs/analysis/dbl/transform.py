""" Transformer for DBL Report Creation """
# pylint: disable=import-error
from io import BytesIO
import logging
import pickle as pk
from string import ascii_uppercase

import numpy as np
import pandas as pd
import xlsxwriter

# pylint: disable=import-error
from datalabs.analysis.dbl.validation import Validater
from   datalabs.task import Task

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


def get_letters_between(start, end):
    return ascii_uppercase[ascii_uppercase.index(start): ascii_uppercase.index(end)+1]


class DBLReportTransformer(Task):
    def run(self) -> 'Transformed Data':
        dataframes = self._get_dataframes(self._data[:10])  # index 10 contains previous report (.xlsx)

        for tab in range(10):
            dataframes[tab] = getattr(self, f"_transform_tab{tab+1}")(dataframes[tab])

        if len(self._data) > 10:
            previous_report = self._data[10]
        else:
            previous_report = None

        output = self._make_excel_workbook(sheet_dataframes=dataframes)

        validater = Validater(output, previous_report)

        validater.validate()

        comparison = {
            'Passing': validater.passing,
            'Log': validater.log,
            'Validations': validater.tab_validations
        }

        # output is returned twice because it's saved to two files, one datestamped, other as "latest" file
        return [output, output, previous_report, pk.dumps(comparison)]

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
        return data.drop_duplicates().fillna('')

    @classmethod
    def _transform_tab2(cls, data):
        """ ReportByFieldFrom SAS """
        # no transformation required
        return data.drop_duplicates().fillna('')

    @classmethod
    def _transform_tab3(cls, data):
        """ ChangeByFieldCount """
        # no transformation required
        return data.drop_duplicates().fillna('')

    @classmethod
    def _transform_tab4(cls, data):
        """ RecordActionExtract """
        # no transformation required
        return data

    @classmethod
    def _transform_tab5(cls, data):
        """ ChangeByRecordCount """
        # no transformation required
        return data.drop_duplicates().fillna('')

    @classmethod
    def _transform_tab6(cls, data):
        """ PE Counts """
        data.drop_duplicates(inplace=True)

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
        data.drop_duplicates(inplace=True)

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
        data.drop_duplicates(inplace=True)

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
        data.drop_duplicates(inplace=True)

        data.columns = ['SPEC Code', 'Description', 'MPA', 'Count']
        table = cls._make_spec_pivot_table(data)
        return table

    @classmethod
    def _transform_tab10(cls, data):
        """ SecSpecbyMPA """
        data.drop_duplicates(inplace=True)

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
        dummy_file = BytesIO()
        output = BytesIO()
        # pylint: disable=abstract-class-instantiated
        writer = pd.ExcelWriter(dummy_file, engine='xlsxwriter')
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

        return output.read()

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

        for sheetname, columns in sheet_column_widths.items():
            for column, width in columns.items():
                workbook.get_worksheet_by_name(sheetname).set_column(column, width)

    @classmethod
    def _format_workbook_percentage_columns(cls, workbook: xlsxwriter.workbook):
        sheet_percentage_columns = {
            'ReportByFieldFrom SAS': ['C:C'],
            'ChangeByRecordCount': ['C:C']
        }

        percentage_format = workbook.add_format({'num_format': '0.00%'})

        for sheet_name, columns in sheet_percentage_columns.items():
            for column in columns:
                workbook.get_worksheet_by_name(sheet_name).set_column(column, 12, percentage_format)