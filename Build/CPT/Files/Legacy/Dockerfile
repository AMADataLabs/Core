# Build Example:
#    docker build --build-arg PACKAGE_NAME=datalabs-oneview-etl-batch --build-arg PACKAGE_VERSION=1.1.0 -t oneview-reindex -f ./Build/OneView/ETL/Batch/Dockerfile ./
FROM eclipse-temurin:18.0.2.1_1-jdk AS build
ARG ENVIRONMENT
ARG PROJECT
ARG AWS_ACCESS_KEY_ID_SANDBOX
ARG AWS_SECRET_ACCESS_KEY_SANDBOX

WORKDIR /Task
ENV AWS_DEFAULT_REGION=us-east-1

RUN export MAVEN_BASE_URL=https://apache.osuosl.org/maven/maven-3
RUN export MAVEN_VERSION=$(curl --silent ${MAVEN_BASE_URL}/ | grep 3.9 | sed 's/^..*href="\([^/][^/]*\)..*/\1/g')

ENV PATH="/Task/apache-maven-${MAVEN_VERSION}/bin:$PATH"

RUN apt update && \
    apt install -y wget software-properties-common && \
    add-apt-repository -y ppa:deadsnakes/ppa && \
    apt update && \
    apt install -y jq unzip python3.9 python3-pip python3.9-venv

RUN curl --fail "${MAVEN_BASE_URL}/${MAVEN_VERSION}/binaries/apache-maven-${MAVEN_VERSION}-bin.tar.gz" -o apache-maven.tar.gz && \
    tar xzf apache-maven.tar.gz

RUN curl --fail "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && \
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

RUN rm -rf ./Build ./Deploy ./Environment ./Script ./Source ./aws ./awscliv2.zip ~/.aws \
    ./apache-maven.tar.gz ./apache-maven-${MAVEN_VERSION}

FROM eclipse-temurin:18.0.2.1_1-jre
WORKDIR /Task
COPY --from=build /Task/Bundle/ /Task
ENV CLASSPATH=/Task:/Task/lib/*
ENV AWS_DEFAULT_REGION=us-east-1
