# Build Example:
#    docker build --build-arg PACKAGE_NAME=datalabs-oneview-etl --build-arg PACKAGE_VERSION=1.1.0 -t oneview-reindex -f ./Build/OneView/ETL/Reindex/Dockerfile ./
FROM python:3.7
ARG PACKAGE_NAME
ARG PACKAGE_VERSION
ARG AWS_ACCESS_KEY_ID
ARG AWS_SECRET_ACCESS_KEY

WORKDIR /OneView
ENV PYTHONPATH=/OneView:/OneView/site-packages
ENV CLASSPATH=/OneView
ENV AWS_DEFAULT_REGION=us-east-1

COPY ./Deploy/Master ./Deploy/Master

RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && \
    unzip awscliv2.zip && \
    ./aws/install

RUN aws configure set profile.default.aws_access_key_id $AWS_ACCESS_KEY_ID && \
    aws configure set profile.default.aws_secret_access_key $AWS_SECRET_ACCESS_KEY && \
    aws configure set profile.default.region us-east-1 && \
    aws configure set profile.default.output json

Deploy/Master/create-python-bundle --project OneView/ETL/Reindex $PACKAGE_NAME==$PACKAGE_VERSION

RUN rm -rf ./Deploy ./aws ./awscliv2.zip
