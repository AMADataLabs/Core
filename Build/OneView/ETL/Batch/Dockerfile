# Build Example:
#    docker build --build-arg PACKAGE_NAME=datalabs-oneview-etl-batch --build-arg PACKAGE_VERSION=1.1.0 -t oneview-reindex -f ./Build/OneView/ETL/Batch/Dockerfile ./
FROM python:3.9
ARG ENVIRONMENT
ARG PROJECT
ARG AWS_ACCESS_KEY_ID_SANDBOX
ARG AWS_SECRET_ACCESS_KEY_SANDBOX

WORKDIR /OneView
ENV PYTHONPATH=/OneView:/OneView/site-packages
ENV CLASSPATH=/OneView
ENV AWS_DEFAULT_REGION=us-east-1

COPY ./Build/Master ./Build/Master
COPY ./Build/OneView/ETL/Batch ./Build/OneView/ETL/Batch
COPY ./Deploy/Master ./Deploy/Master
COPY ./Script ./Script
COPY ./Source/Python/datalabs/build ./Source/Python/datalabs/build

RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && \
    unzip awscliv2.zip && \
    ./aws/install

RUN ./Deploy/Master/setup-aws-cli -e sbx -i $AWS_ACCESS_KEY_ID_SANDBOX -s $AWS_SECRET_ACCESS_KEY_SANDBOX

RUN ./Deploy/Master/create-bundle --environment $ENVIRONMENT --project $PROJECT --no-zip

RUN rm -rf ./Build ./Deploy ./Script ./Source ./aws ./awscliv2.zip

RUN mv ./Bundle/* ./
