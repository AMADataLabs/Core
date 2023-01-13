# Build from repository root
FROM amazonlinux:2.0.20220719.0 as amazon-python
WORKDIR /Build
ARG PYTHON_VERSION=3.9.13
ARG MAVEN_VERSION=3.8.5
ENV MAVEN_HOME=/Build/apache-maven-${MAVEN_VERSION}
ENV M2_HOME=${MAVEN_HOME}
ENV PATH=${MAVEN_HOME}/bin:${PATH}

RUN yum update -y
RUN amazon-linux-extras enable docker
RUN yum -y install openssl-devel bzip2-devel libffi-devel xz-devel freetype-devel sqlite-devel \
    make gcc gcc-c++ sqlite-devel \
    wget tar gzip git xvfb jq docker zip unzip which \
    java-17-amazon-corretto-devel

RUN wget https://www.python.org/ftp/python/${PYTHON_VERSION}/Python-${PYTHON_VERSION}.tgz && \
    tar xzf Python-${PYTHON_VERSION}.tgz && \
    cd Python-${PYTHON_VERSION} && \
    ./configure --enable-optimizations --enable-loadable-sqlite-extensions && \
    make altinstall && \
    ln -s /usr/local/bin/python3.9 /usr/local/bin/python3 && \
    ln -s /usr/local/bin/pip3.9 /usr/local/bin/pip3

RUN yum -y install swig

RUN curl https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip -o awscliv2.zip && \
    unzip awscliv2.zip && \
    ./aws/install && \
    rm -rf aws awscliv2.zip

RUN wget https://archive.apache.org/dist/maven/maven-3/${MAVEN_VERSION}/binaries/apache-maven-${MAVEN_VERSION}-bin.tar.gz && \
    tar xzf ./apache-maven-${MAVEN_VERSION}-bin.tar.gz
