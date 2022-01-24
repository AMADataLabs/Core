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


    def bundle(self, project, version, target_path, extra_files, **kwargs):
        target_path = target_path or Path(os.path.join(self._build_path, project, project)).resolve()

        self._build_bundle(project, version, Path(target_path), extra_files, **kwargs)

    @abstractmethod
    def _build_bundle(self, project, version, target_path, extra_files, **kwargs):
        pass


class LocalProjectBundler(ProjectBundler):
    def _build_bundle(self, project, version, target_path, extra_files, **kwargs):
        if os.path.exists(target_path) and not kwargs['in_place']:
            LOGGER.info('=== Removing Old Target Directory ===')
            shutil.rmtree(target_path)
        LOGGER.debug(kwargs)

        os.makedirs(target_path, exist_ok=True)

        LOGGER.info('=== Copying Build Files ===')
        self._copy_build_files(project, target_path)

        LOGGER.info('=== Generating Project Object Model ===')
        self._render_project_object_model_file(project, version, target_path)

        LOGGER.info('=== Copying Source Files ===')
        self._copy_source_files(project, target_path)

        LOGGER.info('=== Copying Extra Files ===')
        self._copy_extra_files(extra_files, target_path)

        LOGGER.info('=== Creating Jar Archive ===')
        self._jar_source_directory(project, target_path)

    def _copy_build_files(self, project, target_path):
        shutil.copy(os.path.join(self._build_path, 'Master', 'pom.xml.jinja'), os.path.join(target_path, 'pom.xml.jinja'))

    def _render_project_object_model_file(self, project, version, target_path):
        template_path = os.path.join(target_path, 'pom.xml.jinja')
        result_path = os.path.join(target_path, 'pom.xml')

        if not os.path.exists(result_path):
            LOGGER.info(f'Generating file {str(result_path)} from template {str(template_path)}')
            filenames = FileGeneratorFilenames(template=Path(template_path), output=Path(result_path))

            file_generator = SimpleFileGenerator(filenames, project=project, version=version)
            file_generator.generate()

    def _copy_source_files(self, project, target_path):
        modspec_path = os.path.join(self._build_path, project, 'modspec.yaml')
        bundle = JavaSourceBundle.from_file(modspec_path)

        return bundle.copy(self._shared_source_path, os.path.join(target_path, 'src', 'main'))

    def _copy_extra_files(self, files, target_path):
        files = files or []

        for file in files:
            shutil.copy(file, os.path.join(target_path, file))

    def _jar_source_directory(self, project, target_path):
        os.system(f'mvn -f {os.path.join(target_path, "pom.xml")} package')

    def _archive_contents(self, archive, target_path, contents):
        root, dirs, files = contents
        relative_root = Path(root).relative_to(target_path)
        LOGGER.debug('Build Path: %s', target_path)
        LOGGER.debug('Root Path: %s', root)
        LOGGER.debug('Relative Root Path: %s', relative_root)

        for d in dirs:
            archive.write(os.path.join(root, d), arcname=os.path.join(relative_root, d))

        for f in files:
            archive.write(os.path.join(root, f), arcname=os.path.join(relative_root, f))



if __name__ == '__main__':
    return_code = 0

    ap = argparse.ArgumentParser()
    ap.add_argument('-d', '--directory',
        help='Specify the target directory into which files will be bundled (default Build/<PROJECT>/<PROJECT>)')
    ap.add_argument('-i', '--in-place', action='store_true', default=False,
        help='Do not pre-clean the target directory.')
    ap.add_argument(
        '-f', '--file', action='append', required=False, help='Include the given file in the bundle.'
    )
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
            args['version'],
            target_path=args['directory'],
            extra_files=args['file'],
            in_place=args['in_place']
        )
    except Exception as e:
        LOGGER.exception(f"Failed to create project bundle.")
        return_code = 1

    exit(return_code)
