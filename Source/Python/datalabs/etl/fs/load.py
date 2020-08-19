from   datalabs.etl.load import LoaderTask


class LocalFileLoaderTask(LoaderTask):
    def _load(self):
        base_path = self._parameters.variables['PATH']
        files = self._parameters.variables['FILES'].split(',')

        for file, data in zip(files, self._parameters.data):
            self._load_file(base_path, file, data)

    def _load_file(self, base_path, filename, data):
        file_path = os.path.join((base_path, filename))

        with open(file_path, 'wb') as file:
            file.write(data.encode('utf-8'))
