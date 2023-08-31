# Build Example:
#    docker build \
#      --build-arg ENVIRONMENT=sbx \
#      --build-arg PROJECT=CPT/Files/Legacy \
#      --build-arg AWS_ACCESS_KEY_ID_SANDBOX=   \
#      --build-arg AWS_SECRET_ACCESS_KEY_SANDBOX=   \
#      --build-arg MAVEN_VERSION=3.9.3   \
#      -t cpt-files-legacy -f ./Build/CPT/Files/Legacy/Dockerfile ./
FROM eclipse-temurin:18.0.2.1_1-jdk AS build
ARG ENVIRONMENT
ARG PROJECT
ARG AWS_ACCESS_KEY_ID_SANDBOX
ARG AWS_SECRET_ACCESS_KEY_SANDBOX
ARG MAVEN_VERSION=3.9.0

WORKDIR /Task
ENV AWS_DEFAULT_REGION=us-east-1
ENV MAVEN_BASE_URL=https://apache.osuosl.org/maven/maven-3

RUN echo "${MAVEN_BASE_URL}/${MAVEN_VERSION}/binaries/apache-maven-${MAVEN_VERSION}-bin.tar.gz"

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
