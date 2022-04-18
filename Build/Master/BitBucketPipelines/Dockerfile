# Build from repository root
FROM amazonlinux:2.0.20220121.0 as amazon-python
WORKDIR /Build
RUN yum update -y
RUN amazon-linux-extras enable docker
RUN yum -y install gcc openssl-devel bzip2-devel libffi-devel xz-devel make gcc-c++ \
                   python python3-devel python3-pip swig \
                   java-1.8.0-openjdk-devel maven \
                   wget tar gzip git awscli xvfb jq docker unzip which

RUN curl https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip -o awscliv2.zip && \
    unzip awscliv2.zip && \
    ./aws/install && \
    rm -rf aws awscliv2.zip
