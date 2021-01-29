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

from datalabs.build.bundle import SourceBundle

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


class ProjectBundler(ABC):
    def __init__(self, repository_path):
        self._repository_path = repository_path
        self._shared_source_path = Path(os.path.join(self._repository_path, 'Source', 'Python')).resolve()
        self._build_path = Path(os.path.join(self._repository_path, 'Build')).resolve()


    def bundle(self, project, target_path=None, **kwargs):
        target_path = target_path or Path(os.path.join(self._build_path, project, project)).resolve()

        self._build_bundle(project, Path(target_path), **kwargs)

    @abstractmethod
    def _build_bundle(self, project, target_path, **kwargs):
        pass


class LocalProjectBundler(ProjectBundler):
    def _build_bundle(self, project, target_path, **kwargs):
        if os.path.exists(target_path) and not kwargs['in_place']:
            LOGGER.info('=== Removing Old Target Directory ===')
            shutil.rmtree(target_path)

        os.makedirs(target_path, exist_ok=True)

        LOGGER.info('=== Copying Build Files ===')
        self._copy_build_files(project, target_path)

        LOGGER.info('=== Copying Source Files ===')
        self._copy_source_files(project, target_path)

        LOGGER.info('=== Copying Lambda Function Handler ===')
        self._copy_lambda_function_handler(target_path)

        LOGGER.info('=== Copying Local Task Script ===')
        self._copy_local_task_script(target_path)

        LOGGER.info('=== Creating Zip Archive ===')
        self._zip_bundle_directory(project, target_path)

    def _copy_build_files(self, project, target_path):
        self._copy_alembic_files(project, target_path)

        shutil.copy(os.path.join(self._build_path, 'Master', 'settings.py'), os.path.join(target_path, 'settings.py'))

    def _copy_source_files(self, project, target_path):
        modspec_path = os.path.join(self._build_path, project, 'modspec.yaml')
        bundle = SourceBundle(modspec_path)

        return bundle.copy(self._shared_source_path, target_path)

    def _copy_lambda_function_handler(self, target_path):
        shutil.copy(os.path.join(self._build_path, 'Master', 'awslambda.py'), os.path.join(target_path, 'awslambda.py'))

    def _copy_local_task_script(self, target_path):
        shutil.copy(os.path.join(self._build_path, 'Master', 'task.py'), os.path.join(target_path, 'task.py'))

    def _zip_bundle_directory(self, project, target_path):
        archive_path = target_path.resolve().with_suffix('.zip')

        if os.path.exists(archive_path):
            os.remove(archive_path)

        with ZipFile(archive_path, 'w') as archive:
            for contents in os.walk(target_path):
                self._archive_contents(archive, target_path, contents)

    def _copy_alembic_files(self, project, target_path):
        alembic_path = os.path.join(self._build_path, project, 'alembic')
        target_alembic_path = os.path.join(target_path, 'alembic')

        self._remove_alembic_files(target_alembic_path)

        if os.path.exists(alembic_path):
            shutil.copytree(os.path.join(alembic_path, 'versions'), os.path.join(target_alembic_path, 'versions'))
            shutil.copyfile(os.path.join(alembic_path, 'script.py.mako'), os.path.join(target_alembic_path, 'env.py'))
            shutil.copyfile(os.path.join(alembic_path, 'env.py'), os.path.join(target_alembic_path, 'script.py.mako'))
            shutil.copyfile(alembic_path + '.ini', target_alembic_path + '.ini')

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
    def _build_bundle(self, project, target_path, **kwargs):
        from   docker import from_env

        docker = from_env()

        image, _ = self._generate_serverless_artifact(docker, project)

        self._save_serverless_artifact(docker, image, project, target_path)


    def _generate_serverless_artifact(self, docker, project):
        LOGGER.info('=== Generating Serverless Artifact ===')
        dockerfile_path = os.path.join(self._repository_path, 'Build', 'Master', 'Dockerfile.bundle')

        return docker.images.build(
            path=self._repository_path,
            tag='datalabs-serverless-bundler',
            dockerfile=dockerfile_path,
            buildargs=dict(PROJECT=f'{project}'),
            quiet=False
        )

    def _save_serverless_artifact(self, docker, image, project, target_path):
        import tarfile

        LOGGER.info('=== Saving Serverless Artifact ===')
        artifact_path = target_path.resolve().with_suffix('.zip')

        archive = DockerArchive(docker, image.tags[0], '/Build/Bundle.zip')
        tarball = tarfile.open(fileobj=archive)
        artifact = tarball.extractfile('Bundle.zip')

        with open(artifact_path, 'wb') as f:
            for chunk in artifact:
                f.write(chunk)


class DockerArchive(io.BytesIO):
    def __init__(self, docker, image: str, path: str):
        self._docker = docker
        self._image = image
        self._path = path

        super().__init__(self._load())

    def _load(self):
        chunks = []
        container = self._docker.containers.run(self._image, '/bin/bash', detach=True)
        stream, _ = container.get_archive(self._path)

        for chunk in stream:
            chunks.append(chunk)

        try:
            container.kill()
        except Exception:
            pass

        return b''.join(chunks)



if __name__ == '__main__':
    return_code = 0

    ap = argparse.ArgumentParser()
    ap.add_argument('-d', '--directory',
        help='Specify the target directory into which files will be bundled (default Build/<PROJECT>/<PROJECT>)')
    ap.add_argument('-i', '--in-place', action='store_true', default=False,
        help='Do not pre-clean the target directory or try to install dependencies.')
    ap.add_argument('-s', '--serverless', action='store_true', default=False,
        help='Create a zip archive of the bundle for serverless deployment.')
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
            target_path=args['directory'],
            in_place=args['in_place']
        )
    except Exception as e:
        LOGGER.exception(f"Failed to create project bundle.")
        return_code = 1

    exit(return_code)
