# Build from repository root
FROM amazonlinux as amazon-python
WORKDIR /Build
RUN yum -y install gcc openssl-devel bzip2-devel libffi-devel xz-devel wget tar gzip make gcc-c++ \
                   python python3-devel python3-pip git awscli \
                   xvfb jq java-1.8.0-openjdk-devel

COPY Build/Master/BitBucketPipelines/requirements.txt .
RUN pip3.7 install -r requirements.txt
