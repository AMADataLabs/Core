""" Education transformer for creating Education entity """
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


class EducationTransformerTask(Task, CSVReaderMixin, CSVWriterMixin):
    def run(self):
        dataset = self._parse_input(self._data)

        preprocessed_data = self._preprocess_data(dataset)

        entities = self._create_entity(preprocessed_data)

        postprocessed_data = self._postprocess(entities)

        return self._pack(postprocessed_data)

    def _parse_input(self, dataset):
        return [self._csv_to_dataframe(data, sep=",") for data in dataset]

    def _preprocess_data(self, dataset):
        preprocessed_data = [self._columns_to_lower(data) for data in dataset]

        return preprocessed_data

    @classmethod
    def _columns_to_lower(self, data):
        data.rename(columns=lambda x: x.lower(), inplace=True)

        return data

    def _create_entity(self, preprocessed_data):
        (
            medical_education_number,
            ppd_party_ids,
            school_ids,
            school_address_ids,
            school_attendees_details,
            graduate_education_details,
            physician_graduation_year,
            hospital_names,
        ) = preprocessed_data

        ppd_party_ids = ppd_party_ids[["party_id", "me"]]

        hospital_names.thru_dt = pandas.to_datetime(hospital_names.thru_dt)

        hospital_names = hospital_names.sort_values("thru_dt").drop_duplicates(
            "party_hospital_id", keep="last"
        )
        school_ids = school_ids.drop_duplicates()

        graduate_education_details = graduate_education_details.drop_duplicates("party_id")

        extra_school_ids = school_ids[~school_ids.school_id.isin(school_address_ids.school_id)]

        all_school_ids = pandas.concat([school_address_ids, extra_school_ids])

        all_ppd_ids = pandas.merge(
            ppd_party_ids,
            medical_education_number,
            left_on="me",
            right_on="medical_education_number",
        )
        school_address_information = pandas.merge(
            all_school_ids,
            hospital_names,
            left_on="party_id_school",
            right_on="party_hospital_id",
            how="left",
        ).drop_duplicates()
        school_attended_information = pandas.merge(
            school_attendees_details,
            school_address_information,
            left_on="sch_party_id",
            right_on="party_id_school",
            how="left",
        ).drop_duplicates()
        graduate_education_information = pandas.merge(
            graduate_education_details, hospital_names, on="party_hospital_id", how="left"
        ).drop_duplicates()

        school_attended_information = self._reformat_graduate_dates(school_attended_information)

        school_attended_information = self._add_county_and_status_codes(school_attended_information)

        school_attended_information = self._grab_latest_school_attended(school_attended_information)

        education = pandas.merge(all_ppd_ids, physician_graduation_year, on="party_id", how="left")
        education = pandas.merge(education, school_attended_information, on="party_id", how="left")
        education = pandas.merge(
            education,
            graduate_education_information,
            on="party_id",
            how="left",
            suffixes=["_SCH", "_GME"],
        )

        return [education]

    @classmethod
    def _reformat_graduate_dates(self, school_attended_information):
        date_list = []
        for row in school_attended_information.itertuples():
            try:
                new_date = (
                    datetime.strptime(str(row.GRAD_DT), "%d-%b-%Y").date().strftime("%d-%m-%Y")
                )
            except ValueError:
                new_date = None
            date_list.append(new_date)
        school_attended_information["grad_date"] = date_list
        school_attended_information = school_attended_information.sort_values("grad_date")

        return school_attended_information

    @classmethod
    def _add_county_and_status_codes(self, school_attended_information):
        countries = []
        statuses = []
        for row in school_attended_information.itertuples():
            country = 0
            status = 0
            if row.country_id == "6705":
                country = "1"
            if row.sts_type_id == "9":
                status = "2"
            if row.sts_type_id == "54":
                status = "1"
            countries.append(country)
            statuses.append(status)
        school_attended_information["country"] = countries
        school_attended_information["status"] = statuses
        school_attended_information = school_attended_information.sort_values(
            ["status", "country", "grad_date"]
        )

        return school_attended_information

    @classmethod
    def _grab_latest_school_attended(self, school_attended_information):
        singular_school_attended = school_attended_information.drop_duplicates(
            "party_id", keep=False
        )
        multiple_school_attended = school_attended_information[
            school_attended_information.duplicated("party_id", keep=False)
        ]
        latest_school_attended = multiple_school_attended.drop_duplicates("party_id", keep="last")
        school_attended_information = pandas.concat(
            [singular_school_attended, latest_school_attended]
        )

        return school_attended_information

    # pylint: disable=no-self-usegme_singular
    def _postprocess(self, entities):
        entities[0].drop(columns=["me", "grad_dt"], inplace=True)

        return entities

    def _pack(self, postprocessed_data):
        return [
            self._dataframe_to_csv(data, quoting=csv.QUOTE_NONNUMERIC)
            for data in postprocessed_data
        ]
