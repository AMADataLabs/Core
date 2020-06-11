CWD=$(shell realpath .)
RUN=env VIRTUAL_ENV="${CWD}/Environment/Master" python ${CWD}/Script/run.py
TEMPLATE_FILES=${CWD}/Build/Master/requirements_template.txt ${CWD}/Build/Master/Pipfile_template.txt ${CWD}/Build/Master/conda_requirements_template.txt

.PHONY: test

setup:
	./Script/setup_development_environment

test: setup_test_files
	${RUN} python -m pytest Test/Python/ Test/Python/test/datalabs/build/ -W ignore::DeprecationWarning

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
