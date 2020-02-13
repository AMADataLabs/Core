CWD=$(shell realpath .)
RUN=. ${CWD}/Environment/Master/bin/activate; python ${CWD}/Script/run.py
FILES_MASTER=$(shell ls --color=never -1 ${CWD}/Environment/Master | grep -v -e Pipfile -e Pipfile_template.txt -e conda_package_list.txt -e package_list_template.txt -e requirements.txt | tr '\n' ' ')

.PHONY: test

setup:
	./Script/setup_development_environment

env-master:
	${CWD}/Script/setup_python_virtual_environment Environment/Master

clean-master:
	cd ${CWD}/Environment/Master; rm -rf ${FILES_MASTER}

test:
	${RUN} python -m pytest

pythonpath:
	${RUN} printenv PYTHONPATH
