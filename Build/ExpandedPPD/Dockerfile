# Build Example:
#    docker build -t expanded-ppd -f ./Build/ExpandedPPD/Dockerfile \
#                 --build-arg sftp_username=<SFTP Username> --build-arg sftp_password=<SFTP Password> ./

FROM python:3.9.5
WORKDIR /ExpandedPPD
ENV PYTHONPATH=/ExpandedPPD

COPY ./Build/ExpandedPPD/requirements.txt .
RUN pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt

COPY ./Script ./Script
COPY ./Build/Master ./Build/Master
COPY ./Build/ExpandedPPD ./Build/ExpandedPPD
COPY ./Source ./Source

RUN ./Script/bundle-project -i --directory ./ ExpandedPPD

ARG extractor_path="Data Analytics/Baseline/data/expanded"
# Test: "Data Analytics/Test/Baseline/data/expanded"
ENV EXTRACTOR__PATH=${extractor_path}
ARG loader_path="Data Analytics/Data-Science/Data/PPD/Expanded"
# Test: "Data Analytics/Test/Data-Science/Data/PPD/Expanded"
ENV LOADER__PATH=${loader_path}
ARG sftp_username
ARG sftp_password
RUN ./Script/render-template \
    --template ./Build/ExpandedPPD/dotenv_template.txt \
    --file ./.env \
    --vars pythonpath=/ExpandedPPD,sftp_username=${sftp_username},sftp_password=${sftp_password},extractor_path="${extractor_path}",loader_path="${loader_path}"

RUN rm -rf ./Script
RUN rm -rf ./Build
RUN rm -rf ./Source
