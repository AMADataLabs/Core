""" Education transformer for creating Education entity """
from datetime import datetime
import csv
import logging

import pandas
from numpy import nan

from datalabs.task import Task
from datalabs.etl.csv import CSVReaderMixin, CSVWriterMixin
from datalabs.etl.excel import ExcelReaderMixin
from datalabs.analysis.quality.measurement import MeasurementMethods

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class EducationTransformerTask(Task, CSVReaderMixin, CSVWriterMixin):
    def run(self):
        data = [self._csv_to_dataframe(dataset, sep=",") for dataset in self._data]

        preprocessed_data = self._preprocess_data(data)

        education = self._create_education(preprocessed_data)

        return [self._dataframe_to_csv(education, quoting=csv.QUOTE_NONNUMERIC)]

    def _preprocess_data(self, data):
        dataset = [self._columns_to_lower(dataset) for dataset in data]

        ppd_party_ids, hospital_names, school_ids, graduate_education_details, *rest = dataset

        ppd_party_ids = ppd_party_ids[["party_id", "me"]]

        hospital_names.thru_dt = pandas.to_datetime(hospital_names.thru_dt)

        hospital_names = hospital_names.sort_values("thru_dt").drop_duplicates("party_hospital_id", keep="last")
        school_ids = school_ids.drop_duplicates()

        graduate_education_details = graduate_education_details.drop_duplicates("party_id")

        return [ppd_party_ids, hospital_names, school_ids, graduate_education_details] + rest

    @classmethod
    def _columns_to_lower(cls, dataset):
        return dataset.rename(columns=lambda x: x.lower())

    def _create_education(self, preprocessed_data):
        (
            ppd_party_ids,
            hospital_names,
            school_ids,
            graduate_education_details,
            medical_education_number,
            school_address_ids,
            school_attendees_details,
            physician_graduation_year,
        ) = preprocessed_data

        ppd_ids = self._generate_ppd_ids(ppd_party_ids, medical_education_number)

        school_attended = self._generate_school_attended(
            school_ids, school_address_ids, hospital_names, school_attendees_details
        )

        graduate_education = self._generate_graduate_education(graduate_education_details, hospital_names)

        education = self._merge_sub_entities(
            ppd_ids,
            physician_graduation_year,
            school_attended,
            graduate_education,
        )

        return education.drop(columns=["me"]).replace(nan, None)

    @classmethod
    def _generate_ppd_ids(cls, ppd_party_ids, medical_education_number):
        return pandas.merge(ppd_party_ids, medical_education_number, left_on="me", right_on="medical_education_number")

    @classmethod
    def _generate_school_attended(cls, school_ids, school_address_ids, hospital_names, school_attendees_details):
        extra_school_ids = school_ids[~school_ids.school_id.isin(school_address_ids.school_id)]

        all_school_ids = pandas.concat([school_address_ids, extra_school_ids])

        school_address_information = pandas.merge(
            all_school_ids,
            hospital_names,
            left_on="party_id_school",
            right_on="party_hospital_id",
            how="left",
        ).drop_duplicates()

        school_attended = pandas.merge(
            school_attendees_details,
            school_address_information,
            left_on="sch_party_id",
            right_on="party_id_school",
            how="left",
        ).drop_duplicates()

        school_attended["grad_dt"] = (
            school_attended["grad_dt"]
            .replace(nan, None)
            .apply(lambda x: datetime.strptime(str(x), "%d-%b-%Y").strftime("%Y-%m-%d") if x else None)
        )

        school_attended = school_attended.sort_values("grad_dt")

        school_attended = cls._add_county_and_status_codes(school_attended)

        return cls._extract_latest_school_attended(school_attended)

    @classmethod
    def _generate_graduate_education(cls, graduate_education_details, hospital_names):
        graduate_education = pandas.merge(
            graduate_education_details, hospital_names, on="party_hospital_id", how="left"
        ).drop_duplicates()

        graduate_education["begin_dt"] = (
            graduate_education["begin_dt"]
            .replace(nan, None)
            .apply(lambda x: datetime.strptime(str(x), "%d-%b-%Y").strftime("%Y-%m-%d") if x else None)
        )

        graduate_education["end_dt"] = (
            graduate_education["end_dt"]
            .replace(nan, None)
            .apply(lambda x: datetime.strptime(str(x), "%d-%b-%Y").strftime("%Y-%m-%d") if x else None)
        )

        return graduate_education

    @classmethod
    def _add_county_and_status_codes(cls, school_attended_information):
        school_attended_information["country"] = school_attended_information["country_id"].apply(
            lambda x: "1" if str(x) == "6705" else "0"
        )

        school_attended_information["status"] = school_attended_information["sts_type_id"].apply(
            lambda x: "2" if str(x) == "9" else "1" if str(x) == "54" else "0"
        )

        school_attended_information = school_attended_information.sort_values(["status", "country", "grad_dt"])

        return school_attended_information

    @classmethod
    def _extract_latest_school_attended(cls, school_attended_information):
        singular_school_attended = school_attended_information.drop_duplicates("party_id", keep=False)

        multiple_school_attended = school_attended_information[
            school_attended_information.duplicated("party_id", keep=False)
        ]

        latest_school_attended = multiple_school_attended.drop_duplicates("party_id", keep="last")

        school_attended_information = pandas.concat([singular_school_attended, latest_school_attended])

        return school_attended_information

    @classmethod
    def _merge_sub_entities(
        cls,
        ppd_ids,
        physician_graduation_year,
        school_attended,
        graduate_education,
    ):
        education = pandas.merge(ppd_ids, physician_graduation_year, on="party_id", how="left")

        education = pandas.merge(education, school_attended, on="party_id", how="left")

        education = pandas.merge(
            education,
            graduate_education,
            on="party_id",
            how="left",
            suffixes=["_SCH", "_GME"],
        )

        return education


class CompletenessTransformerTask(Task, CSVReaderMixin, CSVWriterMixin, ExcelReaderMixin, MeasurementMethods):
    def run(self):
        input_data = self._parse_input(self._data)

        preprocessed_data = self._preprocess_data(input_data)

        education_completeness = self._create_education_completeness(preprocessed_data)

        postprocessed_data = self._postprocess(education_completeness)

        return self._pack(postprocessed_data)

    def _parse_input(self, data):
        education_entity, measurement_methods = data

        education_entity = self._csv_to_dataframe(education_entity)

        measurement_methods = self._excel_to_dataframe(measurement_methods)

        return [education_entity, measurement_methods]

    def _preprocess_data(self, input_data):
        education_entity, measurement_method_configuration = self._convert_to_lower_case(input_data)

        measurement_method_configuration = self._all_elements_to_lower(measurement_method_configuration)

        return [education_entity, measurement_method_configuration]

    @classmethod
    def _all_elements_to_lower(cls, data):
        return data.applymap(lambda x: x.lower() if isinstance(x, str) else x)

    @classmethod
    def _convert_to_lower_case(cls, data):
        return [dataset.rename(columns=lambda x: x.lower()) for dataset in data]

    @classmethod
    def _create_education_completeness(cls, preprocessed_data):
        education_entity, measurement_methods_configuration = preprocessed_data

        measurement_methods = MeasurementMethods.create_measurement_methods(
            measurement_methods_configuration, "completeness", "education"
        )

        education_completeness = measurement_methods.measure_completeness(education_entity)

        return [education_completeness]

    # pylint: disable=no-self-use
    def _postprocess(self, education_completeness):
        return education_completeness

    def _pack(self, postprocessed_data):
        return [self._dataframe_to_csv(data, quoting=csv.QUOTE_NONNUMERIC) for data in postprocessed_data]
