from   abc import ABC, abstractmethod
import argparse
import io
import logging
import os
from   pathlib import Path
import re
import shutil
import sys
from   zipfile import ZipFile

from   datalabs.build.bundle.java import JavaSourceBundle
from   datalabs.common.setup import FileGeneratorFilenames, SimpleFileGenerator

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


class ProjectBundler(ABC):
    def __init__(self, repository_path):
        self._repository_path = repository_path
        self._shared_source_path = Path(os.path.join(self._repository_path, 'Source', 'Java')).resolve()
        self._build_path = Path(os.path.join(self._repository_path, 'Build')).resolve()


    def bundle(self, project, package, version, target_path, extra_files, **kwargs):
        target_path = target_path or Path(os.path.join(self._build_path, project, project)).resolve()

        if package is None:
            package = project

        self._build_bundle(project, package, version, Path(target_path), extra_files, **kwargs)

    @abstractmethod
    def _build_bundle(self, project, package, version, target_path, extra_files, **kwargs):
        pass


class LocalProjectBundler(ProjectBundler):
    def _build_bundle(self, project, package, version, target_path, extra_files, **kwargs):
        if os.path.exists(target_path) and not kwargs['in_place']:
            LOGGER.info('=== Removing Old Target Directory ===')
            shutil.rmtree(target_path)
        LOGGER.debug(kwargs)

        os.makedirs(target_path, exist_ok=True)

        LOGGER.info('=== Copying Build Files ===')
        self._copy_build_files(project, target_path, kwargs['use_pom'])

        LOGGER.info('=== Generating Project Object Model ===')
        self._render_project_object_model_file(project, package, version, target_path)

        LOGGER.info('=== Copying Source Files ===')
        self._copy_source_files(project, target_path)

        LOGGER.info('=== Copying Extra Files ===')
        self._copy_extra_files(extra_files, target_path)

        LOGGER.info('=== Creating Jar Archive ===')
        self._jar_source_directory(project, target_path)

    def _copy_build_files(self, project, target_path, use_pom):
        LOGGER.debug('Use Build/%s/pom.xml? %s', project, use_pom)
        if use_pom:
            LOGGER.debug('Copying file %s to %s', os.path.join(self._build_path, project, 'pom.xml'), os.path.join(target_path, 'pom.xml'))
            shutil.copy(os.path.join(self._build_path, project, 'pom.xml'), os.path.join(target_path, 'pom.xml'))
        else:
            shutil.copy(os.path.join(self._build_path, 'Master', 'pom.xml.jinja'), os.path.join(target_path, 'pom.xml.jinja'))

    def _render_project_object_model_file(self, project, package, version, target_path):
        template_path = os.path.join(target_path, 'pom.xml.jinja')
        result_path = os.path.join(target_path, 'pom.xml')
        namespace = 'org.ama-assn.datalabs'

        if ':' in package:
            namespace, package = package.split(':')

        if not os.path.exists(result_path):
            LOGGER.info('Generating file %s from template %s', result_path, template_path)
            filenames = FileGeneratorFilenames(template=Path(template_path), output=Path(result_path))

            file_generator = SimpleFileGenerator(
                filenames,
                project=project,
                namespace=namespace,
                package=package,
                version=version
            )
            file_generator.generate()

    def _copy_source_files(self, project, target_path):
        modspec_path = os.path.join(self._build_path, project, 'modspec.yaml')
        bundle = JavaSourceBundle.from_file(modspec_path)

        return bundle.copy(self._shared_source_path, os.path.join(target_path, 'src', 'main', 'java'))

    def _copy_extra_files(self, files, target_path):
        files = files or []
        destination_directory = os.path.join(target_path, 'src', 'main', 'resources')

        os.makedirs(destination_directory, exist_ok=True)

        for file in files:
            shutil.copy(file, os.path.join(destination_directory, file))

    def _jar_source_directory(self, project, target_path):
        os.system('mvn -f %s package'.format(os.path.join(target_path, "pom.xml")))


if __name__ == '__main__':
    return_code = 0

    ap = argparse.ArgumentParser()
    ap.add_argument('-d', '--directory',
        help='Specify the target directory into which files will be bundled (default Build/<PROJECT>/<PROJECT>)')
    ap.add_argument(
        '-f', '--file', action='append', required=False, help='Include the given file in the bundle.'
    )
    ap.add_argument('-i', '--in-place', action='store_true', default=False,
        help='Do not pre-clean the target directory.')
    ap.add_argument('-p', '--use-pom', action='store_true', default=False,
        help='Use the pom.xml in the Build/<PROJECT>/ directory instead of the default template.')
    ap.add_argument('-P', '--package', required=False, help='Specify the package name.')
    ap.add_argument(
        '-v', '--version', default="1.0.0", help='Version of the bundle (default 1.0.0).'
    )
    ap.add_argument('project', help='Name of the project.')
    args = vars(ap.parse_args())
    LOGGER.debug('Args: %s', args)

    try:
        script_path = Path(sys.argv[0])
        script_base_path = script_path.parent
        repository_path = os.path.join(script_base_path, '..')
        project_bundler = None

        project_bundler = LocalProjectBundler(repository_path)

        return_code = project_bundler.bundle(
            args['project'],
            args['package'],
            args['version'],
            target_path=args['directory'],
            extra_files=args['file'],
            in_place=args['in_place'],
            use_pom=args.get('use_pom', False)
        )
    except Exception as e:
        LOGGER.exception(f"Failed to create project bundle.")
        return_code = 1

    exit(return_code)
