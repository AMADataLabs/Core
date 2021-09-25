""" source: datalabs.etl.oneview.reference.transform """
from   io import BytesIO
import os

import pandas
import pytest

from datalabs.etl.oneview.reference.transform import StaticReferenceTablesTransformerTask


def test_static_reference_tables_are_created_properly():
    transformer = StaticReferenceTablesTransformerTask({})

    csv_data = transformer._transform()

    for csv_datum in csv_data:
        table = pandas.read_csv(BytesIO(csv_datum))

        assert "id" in table
        assert "description" in table
