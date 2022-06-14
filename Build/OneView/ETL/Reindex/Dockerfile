# Build Example:
#    docker build -t oneview-reindex -f ./Build/OneView/ETL/Reindex/Dockerfile ./
FROM python:3.7
ARG PACKAGE_NAME
ARG PACKAGE_VERSION

WORKDIR /OneView
ENV PYTHONPATH=/OneView:/OneView/site-packages
ENV CLASSPATH=/OneView
ENV AWS_DEFAULT_REGION=us-east-1

COPY ./Deploy/Master ./Deploy/Master

# TODO: install AWS CLI v2

RUN aws --profile default codeartifact login --tool pip --domain datalabs --repository datalabs-sbx

RUN echo "$PACKAGE" > requirements.txt
RUN pip install --target Bundle/ -r requirements.txt

RUN rm -rf ./Deploy
