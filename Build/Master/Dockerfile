FROM python:3.7 AS Base
WORKDIR /Master

# Needed for AMA local development builds
COPY ./Build/Master/rootca.pem .
RUN pip config set global.cert rootca.pem

RUN pip install pipenv


FROM Base as PythonDependencies
WORKDIR /Master
COPY ./Environment/Master/Pipfile .
RUN pipenv install


FROM PythonDependencies as Code
WORKDIR /Master
COPY ./Source/ .
COPY ./Test/ .
