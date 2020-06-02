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
            codes = self._update_codes_table(data.code)

            self._update_short_descriptors_table(codes, data.short_descriptor)

            self._update_medium_descriptors_table(codes, data.medium_descriptor)

            self._update_long_descriptors_table(codes, data.long_descriptor)

            self._update_modifier_types_table(data.modifier_type)

            self._update_modifiers_table(data.modifier)

            self._update_consumer_descriptors_table(codes, data.consumer_descriptor)

            self._update_clinician_descriptors_table(data.clinician_descriptor)

            self._update_clinician_descriptor_code_mappings_table(data.clinician_descriptor_code_mapping)

    def _update_codes_table(self, codes):
        LOGGER.info('Processing CPT codes...')
        current_codes = self._get_codes()
        old_codes = [code for code in codes.code if code in current_codes]
        new_codes = [code for code in codes.code if code not in current_codes]

        LOGGER.info('    Adding new codes...')
        for code in new_codes:
            self._session.add(model.Code(code=code))

        self._session.commit()

        return IDs(old_codes, new_codes)

    def _update_short_descriptors_table(self, codes, descriptors):
        LOGGER.info('Processing short descriptors...')
        self._update_descriptors_table(model.ShortDescriptor, codes, descriptors)

        self._session.commit()

    def _update_medium_descriptors_table(self, codes, descriptors):
        LOGGER.info('Processing medium descriptors...')
        self._update_descriptors_table(model.MediumDescriptor, codes, descriptors)

        self._session.commit()

    def _update_long_descriptors_table(self, codes, descriptors):
        LOGGER.info('Processing long descriptors...')
        self._update_descriptors_table(model.LongDescriptor, codes, descriptors)

        self._session.commit()

    def _update_modifier_types_table(self, modifier_types):
        LOGGER.info('Processing modifier types...')
        current_modifier_types = self._get_modifier_types()

        LOGGER.info('    Adding new modifier types...')
        for modifier_type in modifier_types.name:
            if modifier_type not in current_modifier_types:
                self._session.add(
                    model.ModifierType(name=modifier_type)
                )

        self._session.commit()

    def _update_modifiers_table(self, modifiers):
        LOGGER.info('Processing modifiers...')
        current_modifier_types = self._get_modifier_types()
        current_modifiers = self._get_modifiers()

        self._update_modifiers(modifiers, current_modifiers)

        self._add_modifiers(modifiers, current_modifiers, current_modifier_types)

        self._session.commit()

    def _update_consumer_descriptors_table(self, codes, descriptors):
        LOGGER.info('Processing consumer descriptors...')
        self._update_descriptors_table(model.ConsumerDescriptor, codes, descriptors)

        self._session.commit()

    def _update_clinician_descriptors_table(self, descriptors):
        LOGGER.info('Processing clinician descriptors...')
        current_descriptors = self._get_clinician_descriptors()
        new_descriptors = {
            id:descriptors[descriptors.id == id]
            for id in descriptors.id
            if id not in current_descriptors
        }

        missing_ids = self._update_descriptors(
            model.ClinicianDescriptor, 'id', current_descriptors.keys(), descriptors, current_descriptors
        )

        self._add_clinician_descriptors(list(new_descriptors.keys()) + missing_ids, descriptors)

        self._session.commit()

    def _update_clinician_descriptor_code_mappings_table(self, mappings):
        LOGGER.info('Processing clinician descriptor code mappings...')
        current_codes = self._get_codes()
        current_mappings = self._get_clinician_descriptor_code_mappings()
        new_mappings = {
            id:mappings.code[mappings.clinician_descriptor == id].iloc[0]
            for id in mappings.clinician_descriptor
            if id not in current_mappings
        }

        self._add_clinician_descriptor_code_mappings(new_mappings, current_codes)

        self._session.commit()

    def _get_codes(self):
        query = self._session.query(model.Code)

        return {row.code:row for row in query.all()}

    def _update_descriptors_table(self, model_class, codes, descriptors):
        LOGGER.info('    Fetching current descriptors...')
        codes.new = codes.new.copy()
        current_descriptors = self._get_descriptors(model_class)

        missing_codes = self._update_descriptors(model_class, 'code', codes.old, descriptors, current_descriptors)

        self._add_descriptors(model_class, codes.new + missing_codes, descriptors)

    def _get_modifier_types(self):
        query = self._session.query(model.ModifierType)

        return {row.name:row for row in query.all()}

    def _get_modifiers(self):
        query = self._session.query(model.Modifier)

        return {row.modifier:row for row in query.all()}

    @classmethod
    def _update_modifiers(cls, modifiers, current_modifiers):
        LOGGER.info('    Updating old modifiers...')
        old_modifiers = [modifier for modifier in modifiers.modifier if modifier in current_modifiers]

        for modifier in old_modifiers:
            if modifier not in current_modifiers:
                missing_modifiers.append(modifier)
            else:
                cls._update_descriptor('modifier', modifier, modifiers, current_modifiers)

    def _add_modifiers(self, modifiers, current_modifiers, modifier_types):
        LOGGER.info('    Adding new modifiers...')
        new_modifiers = [modifier for modifier in modifiers.modifier if modifier not in current_modifiers]
        LOGGER.debug('New Modifiers: %s', new_modifiers)

        for modifier in new_modifiers:
            modifier_details = modifiers[modifiers.modifier == modifier].iloc[0]
            modifier_type = modifier_types[modifier_details.type]
            descriptor = modifier_details.descriptor

            self._session.add(model.Modifier(modifier=modifier, type=modifier_type.id, descriptor=descriptor))

    def _get_clinician_descriptors(self):
        query = self._session.query(model.ClinicianDescriptor)

        return {row.id:row for row in query.all()}

    def _get_clinician_descriptor_code_mappings(self):
        query = self._session.query(model.ClinicianDescriptorCodeMapping)

        return {row.clinician_descriptor:row for row in query.all()}

    def _add_clinician_descriptors(self, new_ids, descriptors):
        LOGGER.info('    Adding new descriptors...')
        for id in new_ids:
            matches = descriptors[descriptors.id == id]

            if len(matches) == 0:
                LOGGER.warn('No %s for code "%s".', model.ClinicianDescriptor.__name__, id)
                continue
            else:
                LOGGER.debug('Adding Clinician Descriptor with id %s', id)

            self._session.add(model.ClinicianDescriptor(id=id, descriptor=matches.descriptor.iloc[0]))

    def _add_clinician_descriptor_code_mappings(self, mappings, codes):
        LOGGER.info('    Adding new mappings...')
        for id, code in mappings.items():
            if code not in codes:
                LOGGER.warn('Ignoring mapping of Clinician Descriptor %s to non-existant CPT code %s', id, code)
                continue
            else:
                LOGGER.debug('Mapping Clinician Descriptor with id %s to CPT code %s', id, code)

            self._session.add(model.ClinicianDescriptorCodeMapping(clinician_descriptor=id, code=code))

    def _get_descriptors(self, model_class):
        query = self._session.query(model_class)

        return {row.code:row for row in query.all()}

    @classmethod
    def _update_descriptors(cls, model_class, primary_key_name, old_primary_keys, descriptors, current_descriptors):
        LOGGER.info('    Updating old descriptors...')
        missing_primary_keys = []

        for primary_key in old_primary_keys:
            if primary_key not in current_descriptors:
                missing_primary_keys.append(primary_key)
            else:
                cls._update_descriptor(primary_key_name, primary_key, descriptors, current_descriptors)

        return missing_primary_keys

    def _add_descriptors(self, model_class, new_codes, descriptors):
        LOGGER.info('    Adding new descriptors...')
        for code in new_codes:
            matches = descriptors.descriptor[descriptors.code == code]

            if len(matches) == 0:
                LOGGER.warn('No %s for code "%s".', model_class.__name__, code)
                continue

            descriptor = matches.iloc[0]

            self._session.add(model_class(code=code, descriptor=descriptor))

    @classmethod
    def _update_descriptor(cls, primary_key_name, primary_key, descriptors, current_descriptors):
        descriptor = descriptors.descriptor[descriptors[primary_key_name] == primary_key].iloc[0]

        if current_descriptors[primary_key] != descriptor:
            current_descriptors[primary_key].descriptor = descriptor
