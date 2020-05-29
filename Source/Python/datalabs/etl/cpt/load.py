""" CPT ETL Loader classes """
from   dataclasses import dataclass
import logging

# import pandas

from datalabs.access.orm import Database
from   datalabs.etl.load import Loader
import datalabs.etl.cpt.dbmodel as model
import datalabs.etl.cpt.transform as transform

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


@dataclass
class IDs:
    old: list
    new: list


class CPTRelationalTableLoader(Loader):
    def __init__(self, configuration):
        super().__init__(configuration)

    def load(self, data: transform.OutputData):
        with Database(key=self._configuration['DATABASE']) as database:
           self._session = database.session

           self._update_tables(data)

    def _update_tables(self, data: transform.OutputData):
            codes = self._update_codes(data.code)

            self._update_short_descriptors(codes, data.short_descriptor)

            self._update_medium_descriptors(codes, data.medium_descriptor)

            self._update_long_descriptors(codes, data.long_descriptor)

            self._update_modifier_types(data.modifier_type)

            self._update_modifiers(data.modifier)

            self._update_consumer_descriptors(codes, data.consumer_descriptor)

            # self._update_clinician_descriptors(data.clinician_descriptor)

            # self._update_clinician_descriptor_code_mappings(data.clinician_descriptor_code_mapping)

            self._session.commit()

    def _update_codes(self, codes):
        query = self._session.query(model.Code)
        current_code_rows = {row.code:row for row in query.all()}
        old_codes = [code for code in codes.code if code in current_code_rows]
        new_codes = [code for code in codes.code if code not in current_code_rows]

        for code in new_codes:
            self._session.add(model.Code(code=code))

        return IDs(old_codes, new_codes)

    def _update_short_descriptors(self, codes, descriptors):
        self._update_descriptors(model.ShortDescriptor, codes, descriptors)

    def _update_medium_descriptors(self, codes, descriptors):
        self._update_descriptors(model.MediumDescriptor, codes, descriptors)

    def _update_long_descriptors(self, codes, descriptors):
        self._update_descriptors(model.LongDescriptor, codes, descriptors)

    def _update_modifier_types(self, modifier_types):
        pass

    def _update_modifiers(self, modifiers):
        pass

    def _update_consumer_descriptors(self, codes, descriptors):
        self._update_descriptors(model.ConsumerDescriptor, codes, descriptors)

    def _update_descriptors(self, model_class, codes, descriptors):
        codes.new = codes.new.copy()
        query = self._session.query(model_class)
        current_descriptors = {row.code:row for row in query.all()}

        missing_codes = self._update_old_descriptors(model_class, codes.old, descriptors, current_descriptors)

        self._add_new_descriptors(model_class, codes.new + missing_codes, descriptors, current_descriptors)

    @classmethod
    def _update_old_descriptors(cls, model_class, old_codes, descriptors, current_descriptors):
        missing_codes = []

        for code in old_codes:
            descriptor = descriptors.descriptor[descriptors.code == code].iloc[0]

            if code not in current_descriptors:
                missing_codes.append(code)
            elif current_descriptors[code] != descriptor:
                current_descriptors[code].descriptor = descriptor

        return missing_codes

    def _add_new_descriptors(self, model_class, new_codes, descriptors, current_descriptors):
        for code in new_codes:
            matches = descriptors.descriptor[descriptors.code == code]

            if len(matches) == 0:
                LOGGER.warn('No %s for code "%s".', model_class.__class__.__name__, code)
                continue

            descriptor = matches.iloc[0]

            self._session.add(model_class(code=code, descriptor=descriptor))
