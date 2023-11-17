""" Mixins for preprocessing data """
from datetime import datetime


class DataProcessingMixin:
    @classmethod
    def _all_elements_to_lower(cls, data):
        return data.applymap(lambda x: x.lower() if isinstance(x, str) else x)

    @classmethod
    def _all_columns_to_lower(cls, data):
        return [dataset.rename(columns=lambda x: x.lower()) for dataset in data]

    @classmethod
    def _rename_column(cls, data, column_mapper):
        return data.rename(columns=column_mapper)

    @classmethod
    def _reformat_date(cls, data, date_format):
        return data.apply(lambda x: datetime.strptime(x, date_format).date() if isinstance(x, str) else x)
