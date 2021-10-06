class ResidencyProgramPhysicianTransformerTask(TransformerTask):
    def _preprocess_data(self, data):
        linked_residency_physician_data = self._linking_data(data)

        linked_residency_physician_data = self._generate_primary_keys(linked_residency_physician_data)

        return [linked_residency_physician_data]

    @classmethod
    def _linking_data(cls, data):
        directors = cls._get_directors(data)
        physicians = cls._get_physician(data)

        directors, unique_directors = cls._find_unique(directors)
        all_match, pure_match = cls._get_matches(physicians, unique_directors)
        duplicate_matches, duplicates = cls._create_duplicate_matches(all_match, pure_match, directors)
        linking_data = cls._filter_out_duplicates(duplicate_matches, duplicates)

        return cls._get_programs(linking_data, directors)

    @classmethod
    def _get_matches(cls, physicians, directors):
        all_match = pandas.merge(physicians, directors,
                                 on=['first_name', 'last_name'], suffixes=['_physician', '_residency'])
        pure_match = pandas.merge(physicians,
                                  directors,
                                  on=['first_name', 'last_name'],
                                  suffixes=['_ppd', '_residency']).drop_duplicates('person_id', keep=False)

        return all_match, pure_match

    @classmethod
    def _create_duplicate_matches(cls, all_match, pure_match, directors):
        duplicate_matches = all_match[~all_match.person_id.isin(pure_match.person_id)]
        duplicates = directors[directors.person_id.isin(duplicate_matches.person_id)]
        duplicate_matches = duplicate_matches.fillna('None')

        return duplicate_matches, duplicates

    @classmethod
    def _get_directors(cls, data):
        data[0] = data[0].fillna('None')
        data[0]['first_name'] = [x.upper() for x in data[0].first_name]
        data[0]['last_name'] = [x.upper() for x in data[0].last_name]

        return data[0]

    @classmethod
    def _get_physician(cls, data):
        data[1]['degree'] = ['MD' if x == 1 else 'DO' for x in data[1].degree_type]

        return data[1]

    @classmethod
    def _find_unique(cls, directors):
        identifying_fields = ['pers_name_last','pers_name_first','pers_name_mid','pers_deg1','pers_deg2','pers_deg3']
        unique_directors = directors.drop_duplicates(identifying_fields).sort_values('pers_name_last')
        unique_directors = unique_directors[identifying_fields]
        unique_directors['person_id'] = list(range(len(unique_directors)))
        directors = pandas.merge(directors, unique_directors, on = [identifying_fields])

        return directors, unique_directors

    @classmethod
    def _filter_out_duplicates(cls, duplicate_matches, duplicates):
        matched_dict_list = []
        for row in duplicates.itertuples():
            new_df = cls._merge_filtered_dataframe(row, duplicate_matches)

            if len(new_df) == 1:
                matched_dict_list.append({'person_id': row.person_id,
                                          'medical_education_number': list(new_df.medical_education_number)[0]})

        return pandas.DataFrame(matched_dict_list)

    @classmethod
    def _get_programs(cls, linking_data, directors):
        return pandas.merge(linking_data, directors, on='person_id')[['ME','pgm_id']]

    @classmethod
    def _merge_filtered_dataframe(cls, row, duplicate_matches):
        new_df = duplicate_matches[duplicate_matches.person_id == row.person_id]

        if row.degree != 'None' and row.degree_one != 'MPH':
            new_df = new_df[new_df.degree == row.degree_one]

        if len(new_df) > 1 and row.middle_name_residency != 'None':
            if len(row.middle_name_residency) == 1:
                new_df['middle'] = [x[0] for x in new_df.middle_name_physician]
                new_df = new_df[new_df.middle == row.middle_name_residency]
            else:
                new_df = new_df[new_df.middle_name_physician == row.middle_name_residency.upper()]

        return new_df

    @classmethod
    def _generate_primary_keys(cls, data):
        primary_keys = [str(column['personnel_member']) + str(column['medical_education_number'])
                        for index, column in data.iterrows()]
        data['pk'] = primary_keys

        return data

    def _get_columns(self):
        return [columns.RESIDENCY_PROGRAM_PHYSICIAN_COLUMNS]