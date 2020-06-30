from   abc import ABC, abstractmethod
import argparse
import logging
import os
from   pathlib import Path
import re
import shutil
import sys
from   zipfile import ZipFile

import jinja2

from datalabs.build.bundle import SourceBundle

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


class ProjectBundler(ABC):
    def __init__(self, repository_path):
        self._repository_path = repository_path
        self._shared_source_path = Path(os.path.join(self._repository_path, 'Source', 'Python')).resolve()

    def bundle(self, project, target_directory=None, **kwargs):
        build_path = Path(os.path.join(self._repository_path, 'Build', args['project'])).resolve()
        target_directory = target_directory or os.path.join(build_path, project)

        self._build_bundle(project, target_directory, **kwargs)

    @abstractmethod
    def _build_bundle(self, project, target_directory, **kwargs):
        pass


class LocalProjectBundler(ProjectBundler):
    def _build_bundle(self, project, target_directory, **kwargs):
        if os.path.exists(target_directory) and not kwargs['inplace']:
            LOGGER.info('=== Removing Old Target Directory ===')
            shutil.rmtree(target_directory)

        os.makedirs(target_directory, exist_ok=True)

        LOGGER.info('=== Copying Build Files ===')
        self._copy_build_files(build_path, target_path)

        LOGGER.info('=== Copying Source Files ===')
        self._copy_source_files()

        if kwargs['verbose']:
            self._log_copied_source_files(relative_file_paths)

        LOGGER.info('=== Creating Zip Archive ===')
        self._zip_bundle_directory(project)

    def _copy_build_files(self):
        copy_alembic_files()

        shutil.copy(os.path.join(build_path, 'settings.py'), os.path.join(target_path, 'settings.py'))

    def _copy_source_files(self):
        modspec_path = os.path.join(build_path, 'modspec.yaml')
        bundle = SourceBundle(modspec_path)

        return bundle.copy(self._shared_source_path, target_directory)

    def _log_copied_source_files(self, relative_file_paths):
        LOGGER.info('Copied the following files from')
        LOGGER.info(self._shared_source_path)
        LOGGER.info(f'    to {target_directory}:')

        for file in relative_file_paths:
            LOGGER.info(file)

    def _zip_bundle_directory(self, project):
        archive_path = os.path.join(build_path, f'{project}.zip')

        if os.path.exists(archive_path):
            os.remove(archive_path)

        with ZipFile(archive_path, 'w') as archive:
            for contents in os.walk(target_directory):
                archive_contents(archive, target_directory, contents)

    def _copy_alembic_files(self):
        alembic_path = os.path.join(build_path, 'alembic')
        target_alembic_path = os.path.join(target_directory, 'alembic')

        remove_alembic_files(target_alembic_path)

        if os.path.exists(alembic_path):
            shutil.copytree(os.path.join(alembic_path, 'versions'), os.path.join(target_alembic_path, 'versions'))
            shutil.copyfile(os.path.join(alembic_path, 'script.py.mako'), os.path.join(target_alembic_path, 'env.py'))
            shutil.copyfile(os.path.join(alembic_path, 'env.py'), os.path.join(target_alembic_path, 'script.py.mako'))
            shutil.copyfile(alembic_path + '.ini', target_alembic_path + '.ini')

    def _archive_contents(self, archive, contents):
        root, dirs, files = contents
        relative_root = root.replace(str(target_directory), '')[1:]
        LOGGER.debug('Build Path: %s', target_directory)
        LOGGER.debug('Root Path: %s', root)
        LOGGER.debug('Relative Root Path: %s', relative_root)

        for d in dirs:
            archive.write(os.path.join(root, d), arcname=os.path.join(relative_root, d))

        for f in files:
            archive.write(os.path.join(root, f), arcname=os.path.join(relative_root, f))


    def _remove_alembic_files(self, target_alembic_path):
        versions_path = os.path.join(target_alembic_path, 'versions')
        env_path = os.path.join(target_alembic_path, 'env.py')
        mako_path = os.path.join(target_alembic_path, 'script.py.mako')

        if os.path.exists(versions_path):
            shutil.rmtree(versions_path)

        if os.path.exists(env_path):
            os.remove(env_path)

        if os.path.exists(mako_path):
            os.remove(mako_path)


class ServerlessProjectBundler(ProjectBundler):
    def _build_bundle(self, project, target_directory, **kwargs):
        from docker import from_env

        docker = from_env()

        image = self._get_bundler_image(docker, project)

        # docker.containers.run(image, )



    def _get_bundler_image(self, docker, project):
        from docker.errors import ImageNotFound

        image = None

        # try:
        #     image = docker.images.get('datalabs-serverless-bundler')
        # except ImageNotFound:
        #     image = self._create_bundler_image(docker)
        image = self._create_bundler_image(docker, project)

        return image


    def _create_bundler_image(self, docker, project):
        LOGGER.info('=== Creating Bundler Docker Image ===')
        dockerfile_path = os.path.join(self._repository_path, 'Build', 'Master', 'Dockerfile.bundle')
        import pdb; pdb.set_trace()
        return docker.images.build(
            path=self._repository_path,
            tag='datalabs-serverless-bundler',
            dockerfile=dockerfile_path,
            buildargs=dict(PROJECT=f'{project}'),
            quiet=False
        )


if __name__ == '__main__':
    return_code = 0

    ap = argparse.ArgumentParser()
    ap.add_argument('-d', '--directory',
        help='Specify the target directory into which files will be bundled (default Build/<PROJECT>/<PROJECT>)')
    ap.add_argument('-i', '--in-place', action='store_true', default=False,
        help='Do not pre-clean the target directory or try to install dependencies.')
    ap.add_argument('-s', '--serverless', action='store_true', default=False,
        help='Create a zip archive of the bundle for serverless deployment.')
    ap.add_argument('-v', '--verbose', action='store_true', default=False,
        help='Verbose output.')
    ap.add_argument('project', help='Name of the project.')
    args = vars(ap.parse_args())
    LOGGER.debug('Args: %s', args)

    try:
        script_path = Path(sys.argv[0])
        script_base_path = script_path.parent
        repository_path = os.path.join(script_base_path, '..')
        project_bundler = None

        if args['serverless']:
            project_bundler = ServerlessProjectBundler(repository_path)
        else:
            project_bundler = LocalProjectBundler(repository_path)

        return_code = project_bundler.bundle(
            args['project'],
            target_directory=args['directory'],
            verbose=args['verbose'],
            inplace=args['in-place']
        )
    except Exception as e:
        LOGGER.exception(f"Failed to create project bundle.")
        return_code = 1

    exit(return_code)
