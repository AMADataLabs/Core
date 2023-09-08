# Build Example:
#    docker build --build-arg PACKAGE_NAME=datalabs-oneview-etl-batch --build-arg PACKAGE_VERSION=1.1.0 -t oneview-reindex -f ./Build/ExpressDAG/ETL/Batch/Dockerfile ./
FROM python:3.9
ARG ENVIRONMENT
ARG PROJECT
ARG AWS_ACCESS_KEY_ID_SANDBOX
ARG AWS_SECRET_ACCESS_KEY_SANDBOX

WORKDIR /ExpressDAG
ENV PYTHONPATH=/ExpressDAG:/ExpressDAG/site-packages
ENV CLASSPATH=/ExpressDAG
ENV AWS_DEFAULT_REGION=us-east-1

RUN apt update && \
    apt install -y jq openjdk-17-jdk

RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && \
    unzip awscliv2.zip && \
    ./aws/install

COPY ./Build/Master ./Build/Master
COPY ./Build/ExpressDAG ./Build/ExpressDAG
COPY ./Deploy/Master ./Deploy/Master
COPY ./Script ./Script
COPY ./Source/Bash/environment/python/setup.sh ./Source/Bash/environment/python/setup.sh
COPY ./Source/Python/datalabs/build ./Source/Python/datalabs/build

RUN ./Deploy/Master/setup-aws-cli -e sbx -i $AWS_ACCESS_KEY_ID_SANDBOX -s $AWS_SECRET_ACCESS_KEY_SANDBOX

RUN ./Deploy/Master/create-bundle --environment $ENVIRONMENT --project $PROJECT --no-zip

RUN apt uninstall -y openjdk-17-jdk
RUN apt uninstall -y openjdk-17-jre

RUN rm -rf ./Build ./Deploy ./Script ./Source ./aws ./awscliv2.zip ~/.aws

RUN mv ./Bundle/* ./
