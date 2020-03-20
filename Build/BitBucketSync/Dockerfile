FROM python:3.7 AS Base
WORKDIR /BitBucketSync

# Needed for AMA local development builds
COPY ./Build/Master/rootca.pem .
RUN pip config set global.cert rootca.pem

RUN pip install pipenv


FROM Base as PythonDependencies
WORKDIR /BitBucketSync

COPY ./Environment/BitBucketSync/Pipfile .
RUN pipenv install


FROM PythonDependencies as Code
WORKDIR /BitBucketSync

COPY ./Source/Python/datalabs .
COPY ./Test/Python/datalabs .
