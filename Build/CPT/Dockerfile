# Build Example:
#    docker build -t cpt -f ./Build/CPT/Dockerfile ./

# FROM python:3.7
FROM amazonlinux
WORKDIR /CPT
RUN yum -y install gcc openssl-devel bzip2-devel libffi-devel xz-devel wget tar
RUN wget https://www.python.org/ftp/python/3.7.7/Python-3.7.7.tgz
RUN tar xzf Python-3.7.7.tgz
RUN cd Python-3.7.7
RUN ./configure --enable-optimizations
RUN make altinstall
RUN cd /CPT
RUN rm- rf Python-3.7.7

# ENV PYTHONPATH=/CPT:/CPT/site-packages
ENV AWS_SHARED_CREDENTIALS_FILE=/CPT/.aws/credentials

COPY ./Build/CPT/requirements.txt .
# RUN pip-3.7 install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt

COPY ./Script ./Script
COPY ./Build/CPT ./Build/CPT
COPY ./Source ./Source
RUN ./Script/bundle-app -i --directory ./ CPT

RUN rm -rf ./Script
RUN rm -rf ./Build
RUN rm -rf ./Source

# COPY ./Test/Python/ .

COPY ./Build/CPT/.env .
COPY ./Build/CPT/credentials ${AWS_SHARED_CREDENTIALS_FILE}
