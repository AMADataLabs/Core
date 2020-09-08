# Build Example:
#    docker build -t one-view -f ./Build/OneView/Dockerfile ./

FROM python:3.7
WORKDIR /OneView
ENV PYTHONPATH=/OneView

COPY ./Build/OneView/requirements.txt .
RUN pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt

COPY ./Script ./Script
COPY ./Build/Master ./Build/Master
COPY ./Build/OneView ./Build/OneView
COPY ./Source ./Source

RUN ./Script/bundle-project -i --directory ./ OneView
RUN ./Script/render-template \
    --template ./Build/OneView/dotenv_template.txt \
    --file ./.env \
    --vars pythonpath=/OneView

RUN rm -rf ./Script
RUN rm -rf ./Build
RUN rm -rf ./Source