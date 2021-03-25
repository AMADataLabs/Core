""" Transformer for DBL Report Creation """

from dataclasses import dataclass
import logging
import numpy as np
import pandas as pd
import settings


from datalabs.etl.transform import TransformerTask

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


@dataclass
class InputData:
    changefileaudit: pd.DataFrame
    reportbyfieldfrom_sas: pd.DataFrame
    changebyfieldcount: pd.DataFrame
    recordactionextract: pd.DataFrame
    changebyrecordcount: pd.DataFrame
    pe_counts: pd.DataFrame
    top_counts: pd.DataFrame
    top_by_pe: pd.DataFrame
    primspecbympa: pd.DataFrame
    secspecbympa: pd.DataFrame


@dataclass
class OutputData:
    changefileaudit: pd.DataFrame
    reportbyfieldfrom_sas: pd.DataFrame
    changebyfieldcount: pd.DataFrame
    recordactionextract: pd.DataFrame
    changebyrecordcount: pd.DataFrame
    pe_counts: pd.DataFrame
    top_counts: pd.DataFrame
    top_by_pe: pd.DataFrame
    primspecbympa: pd.DataFrame
    secspecbympa: pd.DataFrame


class DBLReportTransformer(TransformerTask, InputData):
    def _transform(self) -> 'Transformed Data':
        tab1 = self._transform_tab1()
        tab2 = self._transform_tab2()
        tab3 = self._transform_tab3()
        tab4 = self._transform_tab4()
        tab5 = self._transform_tab5()
        tab6 = self._transform_tab6()
        tab7 = self._transform_tab7()
        tab8 = self._transform_tab8()
        tab9 = self._transform_tab9()
        tab10 = self._transform_tab10()

        return OutputData(
            changefileaudit=tab1,
            reportbyfieldfrom_sas=tab2,
            changebyfieldcount=tab3,
            recordactionextract=tab4,
            changebyrecordcount=tab5,
            pe_counts=tab6,
            top_counts=tab7,
            top_by_pe=tab8,
            primspecbympa=tab9,
            secspecbympa=tab10
        )

    @classmethod
    def _transform_tab1(cls):
        """ ChangeFileAudit """
        return InputData.changefileaudit.fillna('')

    @classmethod
    def _transform_tab2(cls):
        """ ReportByFieldFrom SAS """
        # no transformation required
        return InputData.reportbyfieldfrom_sas

    @classmethod
    def _transform_tab3(cls):
        """ ChangeByFieldCount """
        return InputData.changefileaudit.fillna('')

    @classmethod
    def _transform_tab4(cls):
        """ RecordActionExtract """
        # no transformation required
        return InputData.recordactionextract

    @classmethod
    def _transform_tab5(cls):
        """ ChangeByRecordCount """
        return InputData.changebyrecordcount.fillna('')

    @classmethod
    def _transform_tab6(cls):
        """ PE Counts """
        data = InputData.pe_counts

        data.columns = ['Total', 'PE Code', 'Description']
        data['PE Code'] = data['PE Code'].apply(lambda x: ('000' + str(x))[-3:])

        # re-order columns
        data_formatted = pd.DataFrame()
        formatted_columns = ['PE Code', 'Description', 'Total']
        for col in formatted_columns:
            data_formatted[col] = data[col]

        table = pd.pivot_table(
            data_formatted,
            values='Total',
            index=['PE Code', 'Description'],
            aggfunc=np.sum,
            fill_value=0,
            margins=True
        ).rename(index={'All': 'Grand Total'})

        return table

    @classmethod
    def _transform_tab7(cls):
        """ TOP Counts """
        data = InputData.top_counts

        data.columns = ['Total', 'TOP Code', 'Description']
        data['TOP Code'] = data['TOP Code'].apply(lambda x: ('000' + str(x))[-3:])

        # Re-order columns
        data_formatted = pd.DataFrame()
        formatted_columns = ['TOP Code', 'Description', 'Total']
        for col in formatted_columns:
            data_formatted[col] = data[col]

        table = pd.pivot_table(
            data_formatted,
            values='Total',
            index=['TOP Code', 'Description'],
            aggfunc=np.sum,
            fill_value=0,
            margins=True
        ).rename(index={'All': 'Grand Total'})

        return table

    @classmethod
    def _transform_tab8(cls):
        """ TOP by PE """
        data = InputData.top_by_pe

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
    def _transform_tab9(cls):
        """ PrimSpecbyMPA """
        data = InputData.primspecbympa

        data.columns = ['SPEC Code', 'Description', 'MPA', 'Count']
        table = cls._make_spec_pivot_table(data)
        return table

    @classmethod
    def _transform_tab10(cls):
        """ SecSpecbyMPA """
        data = InputData.secspecbympa

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
