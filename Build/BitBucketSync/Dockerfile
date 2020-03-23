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

COPY ./Source/Python/ .
COPY ./Test/Python/ .

COPY ./Deploy/BitBucketSync/server-ssl.conf .
RUN openssl req --batch -config server-ssl.conf -newkey rsa:2048 -nodes -keyout key.pem -x509 -days 365 -out certificate.pem