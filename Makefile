CWD=$(shell realpath .)
VIRTUAL_ENV=${CWD}/Environment/Master
RUN=env PATH="${VIRTUAL_ENV}/bin:${PATH}" python3 ${CWD}/Script/run.py
#RUN=env VIRTUAL_ENV="${CWD}/Environment/Master" python ${CWD}/Script/run.py
TEMPLATE_FILES=${CWD}/Build/Master/requirements_template.txt ${CWD}/Build/Master/Pipfile_template.txt ${CWD}/Build/Master/conda_requirements_template.txt

.PHONY: test

setup:
	./Script/setup_development_environment

install-go-linux:
	env GOPATH=${CWD}/Source/Go go build -o Script/install-go datalabs/repo/install-go

install-go-windows:
	env GOPATH=${CWD}/Source/Go GOOS=windows GOARCH=amd64 go build -o Script/install-go.exe datalabs/repo/install-go

install-go: install-go-linux install-go-windows

activate-virtual-environment-linux:
	env GOPATH=${CWD}/Source/Go go build -o Script/activate-virtual-environment datalabs/repo/activate-virtual-environment

activate-virtual-environment-windows:
	env GOPATH=${CWD}/Source/Go GOOS=windows GOARCH=amd64 go build -o Script/activate-virtual-environment.exe datalabs/repo/activate-virtual-environment

activate-virtual-environment: activate-virtual-environment-linux activate-virtual-environment-windows

test: setup_test_files
	${RUN} ${VIRTUAL_ENV}/bin/pytest -vv Test/Python/ Test/Python/test/datalabs/build/ -W ignore::DeprecationWarning

setup_test_files: ${TEMPLATE_FILES}
	cp ${TEMPLATE_FILES} ${CWD}/Test/Python/test/datalabs/environment/

clean-test:
	rm -f ${CWD}/Test/Python/test/datalabs/environment/*_template.txt

lint:
	${RUN} pylint --extension-pkg-whitelist=pyodbc,numpy,math $(shell find ${CWD}/Source/Python/datalabs -name "*.py"  | grep -v ${CWD}/Source/Python/datalabs/airflow | tr '\n' ' ') $(shell find ${CWD}/Test/Python/test/datalabs -name "*.py" | tr '\n' ' ')

lint-old:
	${RUN} pylint --extension-pkg-whitelist=pyodbc,numpy --ignore=airflow ${CWD}/Source/Python/datalabs/* ${CWD}/Test/Python/test/datalabs/*

lint-source:
	${RUN} pylint --extension-pkg-whitelist=pyodbc,numpy ${CWD}/Source/Python/datalabs/*

lint-test:
	${RUN} pylint --extension-pkg-whitelist=pyodbc,numpy ${CWD}/Test/Python/*

coverage:
	${RUN} coverage run -m pytest Test/Python/ -W ignore::DeprecationWarning

	coverage report

coverage-report:
	coverage report

pythonpath:
	${RUN} printenv PYTHONPATH

hooks:
	git config core.hooksPath .githooks
