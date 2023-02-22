# Build Example:
#    docker build --build-arg PACKAGE_NAME=datalabs-oneview-etl-batch --build-arg PACKAGE_VERSION=1.1.0 -t oneview-reindex -f ./Build/OneView/ETL/Batch/Dockerfile ./
FROM eclipse-temurin:18.0.2.1_1-jdk
ARG ENVIRONMENT
ARG PROJECT
ARG AWS_ACCESS_KEY_ID_SANDBOX
ARG AWS_SECRET_ACCESS_KEY_SANDBOX

WORKDIR /CPT
ENV AWS_DEFAULT_REGION=us-east-1

RUN sudo add-apt-repository ppa:deadsnakes/ppa && \
    sudo apt update && \
    sudo apt install -y jq unzip wget software-properties-common python3.9

RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && \
    unzip awscliv2.zip && \
    ./aws/install && \
    rm -rf ./aws

COPY ./Build/Master ./Build/Master
COPY ./Build/CPT/Files/Legacy ./Build/CPT/Files/Legacy
COPY ./Deploy/Master ./Deploy/Master
COPY ./Script ./Script
COPY ./Source/Bash/environment/python/setup.sh ./Source/Bash/environment/python/setup.sh
COPY ./Source/Python/datalabs/build ./Source/Python/datalabs/build

RUN ./Deploy/Master/setup-aws-cli -e sbx -i $AWS_ACCESS_KEY_ID_SANDBOX -s $AWS_SECRET_ACCESS_KEY_SANDBOX

RUN ./Deploy/Master/create-bundle --environment $ENVIRONMENT --project $PROJECT --no-zip

RUN rm -rf ./Build ./Deploy ./Script ./Source ./aws ./awscliv2.zip ~/.aws

RUN mv ./Bundle/* ./
