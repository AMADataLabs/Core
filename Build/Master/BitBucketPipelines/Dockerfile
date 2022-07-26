# Build from repository root
FROM amazonlinux:2.0.20220426.0 as amazon-python
WORKDIR /Build
ARG MAVEN_VERSION=3.8.5
ENV MAVEN_HOME=/Build/apache-maven-${MAVEN_VERSION}
ENV M2_HOME=${MAVEN_HOME}
ENV PATH=${MAVEN_HOME}/bin:${PATH}

RUN yum update -y
RUN amazon-linux-extras enable docker
RUN yum -y install gcc openssl-devel bzip2-devel libffi-devel xz-devel make gcc-c++ \
                   python python3-devel python3-pip swig \
                   java-1.8.0-openjdk-devel \
                   wget tar gzip git awscli xvfb jq docker unzip which

RUN curl https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip -o awscliv2.zip && \
    unzip awscliv2.zip && \
    ./aws/install && \
    rm -rf aws awscliv2.zip

RUN wget https://archive.apache.org/dist/maven/maven-3/${MAVEN_VERSION}/binaries/apache-maven-${MAVEN_VERSION}-bin.tar.gz && \
    tar xzf ./apache-maven-${MAVEN_VERSION}-bin.tar.gz
