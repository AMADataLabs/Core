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

            # self._update_modifiers(data.modifier)

            self._update_consumer_descriptors(codes, data.consumer_descriptor)

            # self._update_clinician_descriptors(data.clinician_descriptor)

            # self._update_clinician_descriptor_code_mappings(data.clinician_descriptor_code_mapping)

    def _update_codes(self, codes):
        LOGGER.info('Processing CPT codes...')
        query = self._session.query(model.Code)
        current_codes = {row.code:row for row in query.all()}
        old_codes = [code for code in codes.code if code in current_codes]
        new_codes = [code for code in codes.code if code not in current_codes]

        LOGGER.info('Adding new CPT codes...')
        for code in new_codes:
            self._session.add(model.Code(code=code))

        self._session.commit()

        return IDs(old_codes, new_codes)

    def _update_short_descriptors(self, codes, descriptors):
        LOGGER.info('Processing short descriptors...')
        self._update_descriptors(model.ShortDescriptor, codes, descriptors)

        self._session.commit()

    def _update_medium_descriptors(self, codes, descriptors):
        LOGGER.info('Processing medium descriptors...')
        self._update_descriptors(model.MediumDescriptor, codes, descriptors)

        self._session.commit()

    def _update_long_descriptors(self, codes, descriptors):
        LOGGER.info('Processing long descriptors...')
        self._update_descriptors(model.LongDescriptor, codes, descriptors)

        self._session.commit()

    def _update_modifier_types(self, modifier_types):
        LOGGER.info('Processing modifier types...')
        query = self._session.query(model.ModifierType)
        current_modifier_types = [row.name for row in query.all()]

        LOGGER.info('Adding new modifier types...')
        for modifier_type in modifier_types.name:
            if modifier_type not in current_modifier_types:
                self._session.add(
                    model.ModifierType(name=modifier_type)
                )

        self._session.commit()

    @classmethod
    def _modifier_types_to_indices(cls, modifiers, modifier_types):
        return modifiers['type'].apply(lambda x: modifier_types[modifier_types['name'] == x]['id'].values[0])

    def _update_modifiers(self, modifiers):
        LOGGER.info('Processing modifiers...')
        query = self._session.query(model.Modifier)
        current_modifiers = {row.modifier:row for row in query.all()}

        self._update_old_modifiers(modifiers, current_modifiers)

        self._add_new_modifiers(modifiers, current_modifiers)

        self._session.commit()

    def _update_consumer_descriptors(self, codes, descriptors):
        LOGGER.info('Processing consumer descriptors...')
        self._update_descriptors(model.ConsumerDescriptor, codes, descriptors)

        self._session.commit()

    @classmethod
    def _update_old_modifiers(cls, modifiers, current_modifiers):
        LOGGER.info('    Updating old modifiers...')
        old_modifiers = [modifier for modifier in modifiers.modifier if modifier in current_modifiers]

        for modifier in old_modifiers:
            if modifier not in current_modifiers:
                missing_modifiers.append(modifier)
            else:
                cls._update_old_descriptor(modifier, modifiers, current_modifiers)

    def _add_new_modifiers(self, modifiers, current_modifiers):
        LOGGER.info('    Adding new modifiers...')
        new_modifiers = [modifier for modifier in modifiers.modifier if modifier not in current_modifiers]

        for modifier in new_modifiers:
            modifier = descriptors.descriptor[modifiers.modifier == modifier].iloc[0]

            self._session.add(model.Modifier(modifier=code, descriptor=descriptor))

    def _update_descriptors(self, model_class, codes, descriptors):
        LOGGER.info('    Fetching current descriptors...')
        codes.new = codes.new.copy()
        query = self._session.query(model_class)
        current_descriptors = {row.code:row for row in query.all()}

        missing_codes = self._update_old_descriptors(model_class, codes.old, descriptors, current_descriptors)

        self._add_new_descriptors(model_class, codes.new + missing_codes, descriptors, current_descriptors)

    @classmethod
    def _update_old_descriptors(cls, model_class, old_codes, descriptors, current_descriptors):
        LOGGER.info('    Updating old descriptors...')
        missing_codes = []

        for code in old_codes:
            if code not in current_descriptors:
                missing_codes.append(code)
            else:
                cls._update_old_descriptor(code, descriptors, current_descriptors)

        return missing_codes

    def _add_new_descriptors(self, model_class, new_codes, descriptors, current_descriptors):
        LOGGER.info('    Adding new descriptors...')
        for code in new_codes:
            matches = descriptors.descriptor[descriptors.code == code]

            if len(matches) == 0:
                LOGGER.warn('No %s for code "%s".', model_class.__class__.__name__, code)
                continue

            descriptor = matches.iloc[0]

            self._session.add(model_class(code=code, descriptor=descriptor))

    @classmethod
    def _update_old_descriptor(cls, code, descriptors, current_descriptors):
        descriptor = descriptors.descriptor[descriptors.code == code].iloc[0]

        if current_descriptors[code] != descriptor:
            current_descriptors[code].descriptor = descriptor
