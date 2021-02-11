""" CPT ETL Loader classes """
from   dataclasses import dataclass
from   datetime import datetime
from   functools import reduce
import logging

import pandas
import sqlalchemy as sa

from   datalabs.access.orm import Database
import datalabs.etl.cpt.api.transform as transform
from   datalabs.etl.load import LoaderTask
import datalabs.model.cpt.api as dbmodel
import datalabs.task as task

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


@dataclass
class IDs:
    old: list
    new: list


class CPTRelationalTableLoaderTask(LoaderTask, task.DatabaseTaskMixin):
    def __init__(self, parameters):
        super().__init__(parameters)
        self._release = None
        self._codes = None
        self._pla_codes = None
        self._database = None

    def _load(self):
        with self._get_database(Database, self._parameters.variables) as database:
            self._database = database

            self._update_tables(self._parameters.data)

    def _update_tables(self, data: transform.OutputData):
        release_table_updater = ReleaseTableUpdater(self._database)
        release_table_updater.update(data.release)

        TableUpdater(self._database, dbmodel.Code, 'code').update(data.code)

        ReleaseCodeMappingTableUpdater(
            self._database, dbmodel.ReleaseCodeMapping, 'id', dbmodel.Release, 'release'
        ).update(data.release_code_mapping)

        TableUpdater(self._database, dbmodel.ShortDescriptor, 'code').update(data.short_descriptor)

        TableUpdater(self._database, dbmodel.MediumDescriptor, 'code').update(data.medium_descriptor)

        TableUpdater(self._database, dbmodel.LongDescriptor, 'code').update(data.long_descriptor)

        TableUpdater(self._database, dbmodel.ModifierType, 'id', match_columns='name').update(data.modifier_type)

        ModifierTableUpdater(self._database).update(data.modifier)

        TableUpdater(self._database, dbmodel.ConsumerDescriptor, 'code').update(data.consumer_descriptor)

        TableUpdater(self._database, dbmodel.ClinicianDescriptor, 'id').update(data.clinician_descriptor)

        TableUpdater(self._database, dbmodel.ClinicianDescriptorCodeMapping, 'clinician_descriptor').update(
            data.clinician_descriptor_code_mapping
        )

        TableUpdater(self._database, dbmodel.PLADetails, 'code').update(data.pla_details)

        TableUpdater(self._database, dbmodel.Manufacturer, 'id', match_columns='name').update(data.manufacturer)

        TableUpdater(self._database, dbmodel.Lab, 'id', match_columns='name').update(data.lab)

        OneToManyTableUpdater(
            self._database, dbmodel.ManufacturerPLACodeMapping, 'code', dbmodel.Manufacturer, 'manufacturer'
        ).update(
            data.manufacturer_pla_code_mapping
        )

        OneToManyTableUpdater(
            self._database, dbmodel.LabPLACodeMapping, 'code', dbmodel.Lab, 'lab'
        ).update(data.lab_pla_code_mapping)

        self._database.commit()  # pylint: disable=no-member


class TableUpdater:
    def __init__(self, session, model_class: type, primary_key: list, match_columns: str = None):
        self._database = session
        self._model_class = model_class
        self._primary_key = self._force_list(primary_key)
        self._match_columns = self._force_list(match_columns) or self._primary_key

        mapper = sa.inspect(self._model_class)
        self._columns = [column.key for column in mapper.attrs]

    def update(self, data):
        LOGGER.info('Updating table %s...', self._model_class.__table__.name)
        current_models, current_data = self._get_current_data()
        LOGGER.debug('New data: %s', data)

        old_data, new_data = self._differentiate_data(current_data, data)
        self._update_data(current_models, old_data)

        self._add_data(new_data)

    @classmethod
    def _force_list(cls, value):
        if value is not None and not hasattr(value, 'append'):
            value = [value]

        return value

    def _get_current_data(self):
        results = self._database.query(self._model_class).all()

        return results, self._get_query_results_data(results)

    def _differentiate_data(self, current_data, data):
        merged_data = self._merge_data(current_data, data)

        old_data = merged_data[~merged_data.isnull().any(axis=1)]

        partial_data = merged_data[merged_data.isnull().any(axis=1)]

        new_data = self._remove_missing_rows(partial_data)

        if 'deleted' in data:
            # pylint: disable=singleton-comparison
            soft_deleted_data = partial_data[(partial_data.deleted_CURRENT == False) & (partial_data.deleted == True)]
            old_data = pandas.concat([old_data, self._sync_soft_deleted_rows(soft_deleted_data)])

        return old_data, new_data

    def _update_data(self, models, data):
        filtered_data = self._filter_out_unchanged_data(data)

        filtered_models = self._get_matching_models(models, filtered_data)

        self._update_models(filtered_models, filtered_data)

    def _add_data(self, data):
        models = self._create_models(data)

        self._add_models(models)

    def _get_query_results_data(self, results):
        return pandas.DataFrame({column: [getattr(result, column) for result in results] for column in self._columns})

    def _merge_data(self, current_data, data):
        current_data = self._remove_modified_date(current_data)  # set programmatically

        merged_data = pandas.merge(current_data, data, on=self._match_columns, how='outer', suffixes=['_CURRENT', ''])

        merged_data = self._delete_if_missing(merged_data)
        LOGGER.debug('Merged data: %s', merged_data)

        return self._sync_primary_key(merged_data)

    def _remove_missing_rows(self, data):
        reduced_data = self._drop_current_columns(data)

        reduced_data = reduced_data.drop(self._primary_key, axis=1)

        return self._drop_rows_with_null_values(data, reduced_data)

    def _filter_out_unchanged_data(self, data):
        columns = self._get_changeable_columns()
        conditions = [getattr(data, column) != getattr(data, column + '_CURRENT') for column in columns]
        filtered_data = data

        if conditions:
            filtered_data = data[reduce(lambda x, y: x | y, conditions)]
        else:
            filtered_data = pandas.DataFrame(columns=data.columns.values)

        return filtered_data

    def _get_matching_models(self, models, filtered_data):
        model_map = {tuple(getattr(model, part) for part in self._primary_key): model for model in models}
        keys = (getattr(filtered_data, part).tolist() for part in self._primary_key)

        return [model_map[key] for key in zip(*keys)]

    def _update_models(self, models, data):
        LOGGER.info('    Updating %d existing rows...', len(models))
        columns = self._get_changeable_columns()

        for model, row in zip(models, data.itertuples()):
            self._update_model(model, row, columns)

    @classmethod
    def _remove_modified_date(cls, data):
        if 'modified_date' in data:
            data = data.drop('modified_date', axis=1)

        return data

    @classmethod
    def _delete_if_missing(cls, data):
        if 'deleted' in data:
            data.loc[data.deleted.isnull(), 'deleted'] = True

        return data

    def _sync_primary_key(self, data):
        current_primary_key = [part + '_CURRENT' for part in self._primary_key]

        if all(part in data for part in current_primary_key) and self._primary_key != self._match_columns:
            data[self._primary_key] = data[current_primary_key]

        return data

    def _sync_soft_deleted_rows(self, data):
        current_columns = {column.name + '_CURRENT': column.name for column in self._model_class.__table__.columns
                           if column.name != 'deleted'}
        source_columns = [key for key in current_columns.keys() if key in data]
        target_columns = [current_columns[column] for column in source_columns]

        data[target_columns] = data[source_columns]

        return data

    def _drop_current_columns(self, data):
        current_columns = [column.name + '_CURRENT' for column in self._model_class.__table__.columns]
        drop_columns = [column for column in current_columns if column in data]

        return data.drop(drop_columns, axis=1)

    @classmethod
    def _drop_rows_with_null_values(cls, data, reduced_data):
        delete_indices = reduced_data.isnull().any(axis=1)

        return data.drop(data.index[delete_indices])

    def _create_models(self, data):
        return [self._create_model(row) for row in data.itertuples(index=False)]

    def _add_models(self, models):
        LOGGER.info('    Adding %d new rows...', len(models))
        for model in models:
            self._database.add(model)

    def _get_changeable_columns(self):
        columns = self._get_model_columns()

        for part in self._primary_key:
            columns.remove(part)

        if all(column in columns for column in self._match_columns):
            for part in self._match_columns:
                columns.remove(part)

        return columns

    @classmethod
    def _update_model(cls, model, row, columns):
        for column in columns:
            setattr(model, column, getattr(row, column))

        if hasattr(model, 'modified_date'):
            model.modified_date = datetime.utcnow().date()

    def _create_model(self, row):
        columns = self._get_model_columns()
        parameters = {column: getattr(row, column) for column in columns}
        model = self._model_class(**parameters)
        primary_key = [getattr(row, part) for part in self._primary_key]

        # pylint: disable=comparison-with-itself
        if any(part != part for part in primary_key):  # test for NaN
            for part in self._primary_key:
                setattr(model, part, None)

        if hasattr(model, 'modified_date'):
            model.modified_date = datetime.utcnow().date()

        return model

    def _get_model_columns(self):
        mapper = sa.inspect(self._model_class)
        columns = [column.key for column in mapper.attrs]

        if 'modified_date' in columns:
            columns.remove('modified_date')

        return columns


class ReleaseTableUpdater(TableUpdater):
    def __init__(self, session):
        super().__init__(session, dbmodel.Release, 'id', match_columns=['publish_date', 'effective_date'])

        self._current_models = None
        self._new_models = None
        self._release_id = None

    @property
    def release_id(self):
        return self._release_id

    def update(self, data):
        data.effective_date = data.effective_date.astype(str)
        data.publish_date = data.publish_date.astype(str)

        super().update(data)

        self._database.commit()

        if self._new_models:
            self._release_id = self._new_models[-1].id
        else:
            self._release_id = self._current_models[-1].id

    def _get_current_data(self):
        self._current_models, current_data = super()._get_current_data()

        self._current_models.sort(key=lambda x: x.effective_date)

        current_data.effective_date = current_data.effective_date.astype(str)
        current_data.publish_date = current_data.publish_date.astype(str)

        return self._current_models, current_data

    def _add_data(self, data):
        self._new_models = self._create_models(data)

        self._add_models(self._new_models)

    @classmethod
    def _delete_if_missing(cls, data):
        return data


class ReleaseCodeMappingTableUpdater(TableUpdater):
    # pylint: disable=too-many-arguments
    def __init__(self, session, model_class: type, primary_key, many_model_class, many_key):
        super().__init__(session, model_class, primary_key, match_columns=['code'])

        self._many_model_class = many_model_class
        self._many_key = many_key

    def update(self, data):
        data = self._resolve_key_values_to_ids(data)
        super().update(data)

    def _resolve_key_values_to_ids(self, data):
        lookup_data = self._database.query(self._many_model_class).all()
        id_map = self._map_key_values_to_ids(lookup_data)
        data.loc[:, self._many_key] = data[self._many_key].apply(id_map.get)

        return data[~pandas.isnull(data[self._many_key])]

    @classmethod
    def _map_key_values_to_ids(cls, lookup_data):
        id_map = {}
        for lookup_object in lookup_data:
            id_map[lookup_object.effective_date.strftime('%Y-%m-%d')] = lookup_object.id

        return id_map


class ModifierTableUpdater(TableUpdater):
    def __init__(self, session):
        super().__init__(session, dbmodel.Modifier, 'modifier')

        self._modifier_types = None

    def _get_current_data(self):
        self._modifier_types = {type_.name: type_.id for type_ in self._database.query(dbmodel.ModifierType).all()}

        return super()._get_current_data()

    def _merge_data(self, current_data, data):
        merged_data = super()._merge_data(current_data, data)

        merged_data.loc[:, 'type'] = merged_data.type.apply(lambda x: self._modifier_types[x])

        return merged_data


class OneToManyTableUpdater(TableUpdater):
    # pylint: disable=too-many-arguments
    def __init__(self, session, model_class: type, primary_key, many_model_class, many_key):
        super().__init__(session, model_class, primary_key)

        self._many_model_class = many_model_class
        self._many_key = many_key

    def update(self, data):
        data = self._resolve_key_values_to_ids(data)

        super().update(data)

    def _resolve_key_values_to_ids(self, data):
        lookup_data = self._database.query(self._many_model_class).all()
        id_map = self._map_key_values_to_ids(lookup_data)

        data.loc[:, self._many_key] = data[self._many_key].apply(id_map.get)

        return data[~pandas.isnull(data[self._many_key])]

    @classmethod
    def _map_key_values_to_ids(cls, lookup_data):
        id_map = {}

        for lookup_object in lookup_data:
            id_map[lookup_object.name] = lookup_object.id

        return id_map
