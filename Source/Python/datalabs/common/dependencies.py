""" Objects for generating module dependency information. """

from  pydeps import cli, py2depgraph
from  pydeps.target import Target

# Bootstrap pydeps since it wasn't designed to be used programmatically
cli.verbose = cli._mkverbose(0)  # pylint: disable=protected-access


class Dependencies:
    def __init__(self):
        self._graph = None

    @classmethod
    def from_path(cls, path: str):
        dependencies = Dependencies()

        dependencies._graph = py2depgraph.py2dep(
            Target(path),
            max_bacon=10000,
            show_deps=True,
            show_raw_deps=False,
            exclude_exact=[],
            show_cycles=False,
            noise_level=2**65
        )
        # deps = Dependencies.from_path("Source/Python/datalabs/etl/dag/intelligent_platform/token.py")
        # deps = py2depgraph.py2dep(
        #     Target('Source/Python/datalabs/etl/dag/intelligent_platform/token.py'),
        #     max_bacon=10000,
        #     show_deps=True,
        #     show_raw_deps=False,
        #     exclude_exact=[],
        #     show_cycles=False,
        #     noise_level=2**65
        # )
        return dependencies

    def get_datalabs_modules(self):
        return [key.name for key, _ in self._graph if key.name.startswith("datalabs.")]
