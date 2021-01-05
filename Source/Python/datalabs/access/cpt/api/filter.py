from   sqlalchemy import or_, and_

import datalabs.model.cpt.api as dbmodel


class KeywordFilterMixin:
    @classmethod
    def _filter_for_keywords(cls, fields, query, keywords):
        filter_conditions = []

        for field in fields:
            filter_conditions.extend(field.ilike('%{}%'.format(word)) for word in keywords)

        return query.filter(or_(*filter_conditions))



class WildcardFilterMixin:
    @classmethod
    def _filter_for_wildcard(cls, model, query, codes):
        filter_condition = []

        if codes is not None:
            for code in codes:
                filter_condition.append(cls._create_filter_from_code_pattern(model, code))

            query = query.filter(or_(*filter_condition))

        return query

    @classmethod
    def _create_filter_from_code_pattern(cls, model, pattern):
        parts = pattern.split('*')
        prefix = parts[0]
        filter_condition = model.code == prefix

        if len(parts) == 2:
            suffix = parts[1]
            filter_condition = and_(
                model.code.like(f'{prefix}%'),
                model.code.ilike(f'%{suffix}')
            )

        return filter_condition
