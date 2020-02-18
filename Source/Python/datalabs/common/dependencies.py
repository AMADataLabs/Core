from  pydeps import cli, py2depgraph, pydeps
from  pydeps.target import Target

# Bootstrap pydeps since it wasn't designed to be used programmatically
cli.verbose = cli._mkverbose(0)


class Dependencies:
    def __init__(self, path):
        target = Target(path)

        dep_graph = py2depgraph.py2dep(
            target, max_bacon=1, show_deps=True, show_raw_deps=False,
             exclude_exact=[], show_cycles=False, noise_level=2**65
        )

