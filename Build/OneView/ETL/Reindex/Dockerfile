# Build Example:
#    docker build -t oneview-reindex -f ./Build/OneView/ETL/Reindex/Dockerfile ./
FROM python:3.7

WORKDIR /OneView
ENV PYTHONPATH=/OneView:/OneView/site-packages
ENV CLASSPATH=/OneView
ENV AWS_DEFAULT_REGION=us-east-1

COPY ./Build/OneView/ETL/Reindex/requirements.txt .
RUN chown -R root:root /var/lang/lib/python3.7
RUN pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt

COPY ./Script ./Script
COPY ./Build/Master ./Build/Master
COPY ./Build/OneView/ETL/Reindex ./Build/OneView/ETL/Reindex
COPY ./Source/Python ./Source/Python
COPY ./Source/Bash ./Source/Bash

RUN ./Script/bundle-project -i --directory ./ OneView/ETL/Reindex

RUN rm -rf ./Build/Master
RUN rm -rf ./Source
