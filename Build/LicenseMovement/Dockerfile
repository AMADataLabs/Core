# Build Example:
#    docker build -t one-view -f ./Build/LicenseMovement/Dockerfile ./

FROM python:3.7
WORKDIR /LicenseMovement
ENV PYTHONPATH=/LicenseMovement

COPY ./Build/LicenseMovement/requirements.txt .
RUN pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt

COPY ./Script ./Script
COPY ./Build/Master ./Build/Master
COPY ./Build/LicenseMovement ./Build/LicenseMovement
COPY ./Source ./Source

RUN ./Script/bundle-project -i --directory ./ LicenseMovement
RUN ./Script/render-template \
    --template ./Build/LicenseMovement/dotenv_template.txt \
    --file ./.env \
    --vars pythonpath=/LicenseMovement

RUN rm -rf ./Script
RUN rm -rf ./Build
RUN rm -rf ./Source