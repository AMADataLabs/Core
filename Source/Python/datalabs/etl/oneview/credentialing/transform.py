"""Oneview Credentialing Transformer"""
import logging
import pandas

from   datalabs.etl.oneview.transform import TransformerTask

from   datalabs.etl.oneview.credentialing import column

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class CredentialingTransformerTask(TransformerTask):
    def _postprocess(self, dataset):
        products, orders = dataset

        products = products.dropna(subset=['description'])

        orders.date = pandas.to_datetime(orders.date).astype(str)

        return [products, orders]

    def _get_columns(self):
        return [column.PRODUCT_COLUMNS, column.ORDER_COLUMNS]


class CredentialingFinalTransformerTask(TransformerTask):
    def _parse(self, dataset):
        addresses = pandas.read_excel(dataset[0], engine='openpyxl')
        customers = self._csv_to_dataframe(dataset[1], encoding="ISO-8859-1", engine='python')

        return [addresses, customers]

    # pylint: disable=no-self-use
    def _preprocess(self, dataset):
        addresses, customers = dataset[0]

        addresses.rename(columns={'number': 'CUSTOMER_NBR'}, inplace=True)

        return [customers.merge(addresses, how='left', on='number')]

    def _get_columns(self):
        return [column.CUSTOMER_COLUMNS]


class CredentialingOrderPruningTransformerTask(TransformerTask):
    def _preprocess(self, dataset):
        orders, physicians, customers = dataset

        orders = orders[(orders.customer.isin(customers.id))]
        orders = orders[(orders.medical_education_number.isin(physicians.medical_education_number))]

        return [orders.drop_duplicates()]

    def _get_columns(self):
        columns = {value:value for value in column.ORDER_COLUMNS.values()}

        return [columns]
