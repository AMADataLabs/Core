CWD=$(shell realpath .)
RUN=. ${CWD}/Environment/Master/bin/activate; python ${CWD}/Script/run.py
FILES_MASTER=$(shell ls --color=never -1 ${CWD}/Environment/Master | grep -v -e Pipfile -e Pipfile_template.txt -e conda_package_list.txt -e package_list_template.txt -e requirements.txt | tr '\n' ' ')
TEMPLATE_FILES=${CWD}/Environment/Master/requirements_template.txt ${CWD}/Environment/Master/Pipfile_template.txt ${CWD}/Environment/Master/conda_requirements_template.txt

.PHONY: test

setup:
	./Script/setup_development_environment

env-master:
	${CWD}/Script/setup_python_virtual_environment Environment/Master

clean-master:
	cd ${CWD}/Environment/Master; rm -rf ${FILES_MASTER}

test: setup_test_files
	${RUN} python -m pytest Test/Python/

setup_test_files: ${TEMPLATE_FILES}
	cp ${TEMPLATE_FILES} ${CWD}/Test/Python/datalabs/test/environment/

clean-test:
	rm -f ${CWD}/Test/Python/datalabs/test/environment/*_template.txt

lint:
	${RUN} pylint --extension-pkg-whitelist=pyodbc,numpy ${CWD}/Source/Python/*

lint-test:
	${RUN} pylint --extension-pkg-whitelist=pyodbc,numpy ${CWD}/Test/Python/*

pythonpath:
	${RUN} printenv PYTHONPATH
