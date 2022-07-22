# Build Example:
#    docker build --build-arg PACKAGE_NAME=datalabs-oneview-etl --build-arg PACKAGE_VERSION=1.1.0 -t oneview-reindex -f ./Build/OneView/ETL/Reindex/Dockerfile ./
FROM python:3.7
ARG PACKAGE_NAME
ARG PACKAGE_VERSION
ARG AWS_ACCESS_KEY_ID_SANDBOX
ARG AWS_SECRET_ACCESS_KEY_SANDBOX

WORKDIR /OneView
ENV PYTHONPATH=/OneView:/OneView/site-packages
ENV CLASSPATH=/OneView
ENV AWS_DEFAULT_REGION=us-east-1

COPY ./Build/Master ./Build/Master
COPY ./Build/OneView/ETL/Reindex ./Build/OneView/ETL/Reindex
COPY ./Deploy/Master ./Deploy/Master
COPY ./Script ./Script
COPY ./Source/Python/datalabs/build ./Source/Python/datalabs/build

RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && \
    unzip awscliv2.zip && \
    ./aws/install

RUN pip install -r Build/Master/Docker/requirements.txt

RUN aws configure set profile.sandbox.aws_access_key_id $AWS_ACCESS_KEY_ID_SANDBOX && \
    aws configure set profile.sandbox.aws_secret_access_key $AWS_SECRET_ACCESS_KEY_SANDBOX && \
    aws configure set profile.sandbox.region us-east-1 && \
    aws configure set profile.sandbox.output json

RUN aws --profile sandbox codeartifact login --tool pip --domain datalabs --repository datalabs-sbx

RUN pip install $PACKAGE_NAME==$PACKAGE_VERSION
RUN cp ./Build/Master/settings.py ./settings.py
RUN cp ./Build/Master/task.py ./task.py

RUN rm -rf ./Build ./Deploy ./Script ./Source ./aws ./awscliv2.zip
