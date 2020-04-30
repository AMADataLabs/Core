CWD=$(shell realpath .)
RUN=. ${CWD}/Environment/Master/bin/activate; python ${CWD}/Script/run.py
TEMPLATE_FILES=${CWD}/Build/Master/requirements_template.txt ${CWD}/Build/Master/Pipfile_template.txt ${CWD}/Build/Master/conda_requirements_template.txt

.PHONY: test

setup:
	./Script/setup_development_environment

build-install-go-linux:
	env GOPATH=${CWD}/Source/Go go build -o Script/install-go datalabs/repo/install-go

build-install-go-windows:
	env GOPATH=${CWD}/Source/Go GOOS=windows GOARCH=amd64 go build -o Script/install-go.exe datalabs/repo/install-go

build-install-go: build-install-go-linux build-install-go-windows

test: setup_test_files
	${RUN} python -m pytest Test/Python/ -W ignore::DeprecationWarning

setup_test_files: ${TEMPLATE_FILES}
	cp ${TEMPLATE_FILES} ${CWD}/Test/Python/test/datalabs/environment/

clean-test:
	rm -f ${CWD}/Test/Python/test/datalabs/environment/*_template.txt

lint:
	${RUN} pylint --extension-pkg-whitelist=pyodbc,numpy ${CWD}/Source/Python/* ${CWD}/Test/Python/*

lint-source:
	${RUN} pylint --extension-pkg-whitelist=pyodbc,numpy ${CWD}/Source/Python/*

lint-test:
	${RUN} pylint --extension-pkg-whitelist=pyodbc,numpy ${CWD}/Test/Python/*

coverage:
	${RUN} coverage run -m pytest Test/Python/ -W ignore::DeprecationWarning

	coverage report

coverage-report:
	coverage report

pythonpath:
	${RUN} printenv PYTHONPATH
