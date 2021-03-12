""" source: datalabs.access.cpt.api.resolve """
from   datalabs.access.cpt.api.resolve import TaskClassMapping, TaskResolver


def test_task_resolver_resolves_wildcard_path_patterns():
    # pylint: disable=bad-whitespace
    TaskResolver.TASK_CLASSES = [
        TaskClassMapping('/ping/pong/*',    'datalabs.fake.module.PongTask'),
        TaskClassMapping('/ping/pongs',     'datalabs.fake.module.PongsTask'),
        TaskClassMapping('/ping/dings/*',   'datalabs.fake.module.DingsTask'),
        TaskClassMapping('/ping/dings',     'datalabs.fake.module.DingsesTask'),
        TaskClassMapping('/*',              'datalabs.fake.module.SomeTask')
    ]

    # pylint: disable=bad-whitespace
    actual_mappings = [
        TaskClassMapping('/ping/pong/123',          'datalabs.fake.module.PongTask'),
        TaskClassMapping('/ping/pongs',             'datalabs.fake.module.PongsTask'),
        TaskClassMapping('/ping/dings/456',         'datalabs.fake.module.DingsTask'),
        TaskClassMapping('/ping/dings',             'datalabs.fake.module.DingsesTask'),
        TaskClassMapping('/wing/ding/biff/baff',    'datalabs.fake.module.SomeTask')
    ]

    for mapping in actual_mappings:
        class_name = TaskResolver.get_task_class_name(dict(path=mapping.path))

        assert class_name == mapping.class_name
