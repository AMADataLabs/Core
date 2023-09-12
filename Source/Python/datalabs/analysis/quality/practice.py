""" Practice transformer class for creating Practice entitiy """
# pylint: disable=import-error
import csv
import logging
import pandas

# pylint: disable=wrong-import-order
from datetime import datetime

from datalabs.task import Task
from datalabs.etl.csv import CSVReaderMixin, CSVWriterMixin

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class PracticeTransformerTask(Task, CSVReaderMixin, CSVWriterMixin):
    def run(self):
        dataset = self._parse_input(self._data)

        preprocessed_data = self._preprocess(dataset)

        entity = self._create_entity(preprocessed_data)

        postprocessed_data = self._postprocess(entity)

        return self._pack(postprocessed_data)

    def _parse_input(self, dataset):
        return [self._csv_to_dataframe(data, sep=",") for data in dataset]

    def _preprocess(self, dataset):
        dataset = [self._convert_columns_to_lower_case(data) for data in dataset]

        return dataset

    @classmethod
    def _convert_columns_to_lower_case(cls, data):
        data.rename(columns=lambda x: x.lower(), inplace=True)

        return data

    # pylint: disable=no-self-use
    def _create_entity(self, preprocessed_data):
        # fmt: off
        medical_education_number, ppd_party_ids, employer_ids, active_mpa_codes, specialities, pra_certifications \
            = preprocessed_data
        # fmt: on

        pra_certifications.expiration_dt = pandas.to_datetime(pra_certifications.expiration_dt)

        wards = (
            pra_certifications[pra_certifications.expiration_dt > datetime.today()]
            .sort_values("expiration_dt")
            .drop_duplicates("party_id", keep="last")
        )

        ov_universe = pandas.merge(
            ppd_party_ids,
            medical_education_number,
            left_on="me",
            right_on="medical_education_number",
        )

        entity = pandas.merge(ov_universe, employer_ids, on="party_id", how="left")

        entity = pandas.merge(
            entity,
            specialities[specialities.prefe_lvl == "1"],
            on="party_id",
            how="left",
        )

        entity = pandas.merge(
            entity,
            specialities[specialities.prefe_lvl == "2"],
            on="party_id",
            suffixes=["_prim", "_sec"],
            how="left",
        )

        entity = pandas.merge(entity, active_mpa_codes, on=["top_id", "employer_id"], how="left")

        entity = pandas.merge(entity, wards, on="party_id", how="left")

        return [entity]

    # pylint: disable=no-self-use
    def _postprocess(self, entity):
        entity[0].drop(columns=["me"], inplace=True)

        return entity

    def _pack(self, postprocessed_data):
        return [self._dataframe_to_csv(data, quoting=csv.QUOTE_NONNUMERIC) for data in postprocessed_data]
