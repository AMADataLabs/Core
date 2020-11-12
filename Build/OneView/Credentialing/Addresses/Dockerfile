# Build Example:
#    docker build -t one-view -f ./Build/OneView/Credentialing/Addresses/Dockerfile ./

FROM python:3.7
WORKDIR /OneView
ENV PYTHONPATH=/OneView:/OneView/site-packages
ENV AWS_SHARED_CREDENTIALS_FILE=/OneView/.aws/credentials
ENV AWS_DEFAULT_REGION=us-east-1

COPY ./Build/OneView/requirements.txt .
RUN pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt

COPY ./Script ./Script
COPY ./Build/Master ./Build/Master
COPY ./Build/OneView ./Build/OneView
COPY ./Source ./Source
RUN ./Script/bundle-project -i --directory ./ OneView

RUN rm -rf ./Script
RUN rm -rf ./Build
RUN rm -rf ./Source

# COPY ./Test/Python/ .

COPY ./Build/OneView/Credentialing/Addresses.env .
COPY ./Build/OneView/credentials ${AWS_SHARED_CREDENTIALS_FILE}