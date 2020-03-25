FROM python:3.7 AS Base
WORKDIR /Master

RUN pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org pipenv


FROM Base as PythonDependencies
WORKDIR /Master

COPY ./Environment/Master/Pipfile .

RUN pipenv install


FROM PythonDependencies as Code
WORKDIR /Master

COPY ./Source/ .
COPY ./Test/ .
