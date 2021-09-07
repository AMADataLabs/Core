""" source: datalabs.access.cpt.api.resolve """
from   datalabs.access.cpt.api.resolve import TaskClassMapping, TaskResolver


class PongTask:
    pass


class PongsTask:
    pass


class DingsTask:
    pass


class DingsesTask:
    pass


class SomeTask:
    pass


def test_task_resolver_resolves_wildcard_path_patterns():
    TaskResolver.TASK_CLASSES = [
        TaskClassMapping('/ping/pong/*',    PongTask),
        TaskClassMapping('/ping/pongs',     PongsTask),
        TaskClassMapping('/ping/dings/*',   DingsTask),
        TaskClassMapping('/ping/dings',     DingsesTask),
        TaskClassMapping('/*',              SomeTask)
    ]

    actual_mappings = [
        TaskClassMapping('/ping/pong/123',          PongTask),
        TaskClassMapping('/ping/pongs',             PongsTask),
        TaskClassMapping('/ping/dings/456',         DingsTask),
        TaskClassMapping('/ping/dings',             DingsesTask),
        TaskClassMapping('/wing/ding/biff/baff',    SomeTask)
    ]

    for mapping in actual_mappings:
        task_class = TaskResolver.get_task_class(dict(path=mapping.path))

        assert task_class == mapping.task_class
