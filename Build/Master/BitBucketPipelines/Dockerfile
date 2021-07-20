# Build from repository root
FROM amazonlinux:2.0.20210617.0 as amazon-python
WORKDIR /Build
RUN yum -y install gcc openssl-devel bzip2-devel libffi-devel xz-devel wget tar gzip make gcc-c++ \
                   python python3-devel python3-pip git awscli \
                   xvfb jq java-1.8.0-openjdk-devel

# RUN rm /usr/bin/python && ln -s /usr/bin/python3.7 /usr/bin/python

COPY Build/Master/BitBucketPipelines/requirements.txt .

RUN cat requirements.txt | grep pip== > pip-requirements.txt &&\
    pip3.7 install -r pip-requirements.txt &&\
    pip install -r requirements.txt
