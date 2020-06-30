# Build Example:
#    docker build -t cpt -f ./Build/CPT/Dockerfile ./

# FROM python:3.7
FROM amazonlinux as amazon-python
WORKDIR /CPT
RUN yum -y install gcc openssl-devel bzip2-devel libffi-devel xz-devel wget tar gzip make
RUN wget https://www.python.org/ftp/python/3.7.7/Python-3.7.7.tgz
RUN tar xzf Python-3.7.7.tgz

WORKDIR /CPT/Python-3.7.7
RUN ./configure --enable-optimizations
RUN make altinstall

WORKDIR /CPT
# RUN rm -rf Python-3.7.7
# RUN rm -rf Python-3.7.7.tgz

COPY ./Build/CPT/requirements.txt .
RUN pip3.7 install --trusted-host pypi.org --trusted-host files.pythonhosted.org --target ./ -r requirements.txt

# FROM amazonlinux as build
# COPY --from=amazon-python 
# RUN python3.7 ./Script/bundle_app.py -i --directory ./ CPT
# COPY ./Script ./Script
# COPY ./Build/CPT ./Build/CPT
# COPY ./Source ./Source
# ENV PYTHONPATH=/CPT:/CPT/Source/Python


# # RUN rm -rf ./Script
# # RUN rm -rf ./Build
# # RUN rm -rf ./Source

# # COPY ./Test/Python/ .

# WORKDIR /CPT
# ENV AWS_SHARED_CREDENTIALS_FILE=/CPT/.aws/credentials
# COPY --from=build /CPT .
# COPY ./Build/CPT/.env .
# COPY ./Build/CPT/credentials ${AWS_SHARED_CREDENTIALS_FILE}

# ENV PYTHONPATH=/CPT
