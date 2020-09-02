# Build Example:
#    docker build -t cpt -f ./Build/CPT/Dockerfile ./

FROM python:3.7
WORKDIR /CPT
ENV PYTHONPATH=/CPT:/CPT/site-packages
ENV AWS_SHARED_CREDENTIALS_FILE=/CPT/.aws/credentials

COPY ./Build/CPT/requirements.txt .
RUN pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt

COPY ./Script ./Script
COPY ./Build/Master ./Build/Master
COPY ./Build/CPT ./Build/CPT
COPY ./Source ./Source
RUN ./Script/bundle-project -i --directory ./ CPT

RUN rm -rf ./Script
RUN rm -rf ./Build
RUN rm -rf ./Source

# COPY ./Test/Python/ .

COPY ./Build/Master/settings.py /CPT
COPY ./Build/CPT/Load/.env .
COPY ./Build/CPT/credentials ${AWS_SHARED_CREDENTIALS_FILE}
