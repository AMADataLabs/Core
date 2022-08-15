package datalabs.etl.sql;

/*
class SQLParametricExtractorTask(CSVReaderMixin, SQLExtractorTask):
    PARAMETER_CLASS = SQLParametricExtractorParameters

    def __init__(self, parameters):
        super().__init__(parameters)

        self._query_parameters = self._csv_to_dataframe(self._parameters.data[0])

    def _read_single_query(self, query, connection):
        resolved_query = self._resolve_query(query, 0, 0)

        return super()._read_single_query(resolved_query, connection)

    def _resolve_query(self, query, record_index, record_count):
        formatter = PartialFormatter()
        resolved_query = query

        if '{index}' in query and '{count}' in query:
            resolved_query = formatter.format(query, index=record_index, count=record_count)

        part_index = int(self._parameters.part_index)
        parameters = self._query_parameters.iloc[part_index].to_dict()

        return formatter.format(resolved_query, **parameters)
*/
