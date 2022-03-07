# Build from repository root
FROM amazonlinux:2.0.20220121.0 as amazon-python
WORKDIR /Build
RUN yum update -y
RUN amazon-linux-extras enable docker
RUN yum -y install gcc openssl-devel bzip2-devel libffi-devel xz-devel wget tar gzip make gcc-c++ \
                   python python3-devel python3-pip git awscli \
                   xvfb jq java-1.8.0-openjdk-devel docker unzip

RUN curl https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip -o awscliv2.zip && \
    unzip awscliv2.zip && \
    ./aws/install && \
    rm -rf aws awscliv2.zip

RUN curl https://www.python.org/ftp/python/3.9.10/Python-3.9.10.tgz -o Python-3.9.10.tgz && \
    tar xzf Python-3.9.10.tgz && \
    cd Python-3.9.10 && \
    ./configure --enable-optimzations && \
    make altinstall && \
    rm -rf /opt/Python-3.9.10.tgz

COPY Build/Master/BitBucketPipelines/requirements.txt .

RUN cat requirements.txt | grep pip== > pip-requirements.txt &&\
    pip3.9 install -r pip-requirements.txt &&\
    pip3.9 install -r requirements.txt
