""" source: datalabs.etl.oneview.reference.transform """
from   io import BytesIO

import pandas

from datalabs.etl.oneview.reference.transform import StaticReferenceTablesTransformerTask


# pylint: disable=protected-access
def test_static_reference_tables_are_created_properly():
    transformer = StaticReferenceTablesTransformerTask({})

    csv_data = transformer._transform()

    for csv_datum in csv_data:
        table = pandas.read_csv(BytesIO(csv_datum))

        assert "id" in table
        assert "description" in table
