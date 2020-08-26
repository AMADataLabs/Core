# Build Example:
#    docker build -t expanded-ppd -f ./Build/ExpandedPPD/Dockerfile ./

FROM python:3.7
WORKDIR /ExpandedPPD
ENV PYTHONPATH=/ExpandedPPD

COPY ./Build/ExpandedPPD/requirements.txt .
RUN pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt

COPY ./Script ./Script
COPY ./Build/Master ./Build/Master
COPY ./Build/ExpandedPPD ./Build/ExpandedPPD
COPY ./Source ./Source

RUN ./Script/bundle-project -i --directory ./ ExpandedPPD
RUN ./Script/render-template \
    --template ./Build/ExpandedPPD/dotenv_template.txt \
    --file ./.env \
    --vars pythonpath=/ExpandedPPD

RUN rm -rf ./Script
RUN rm -rf ./Build
RUN rm -rf ./Source
