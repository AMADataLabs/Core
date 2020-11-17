# Build Example:
#    docker build -t one-view -f ./Build/OneView/PPD/Dockerfile ./

FROM python:3.7
WORKDIR /OneView
ENV PYTHONPATH=/OneView:/OneView/site-packages
ENV CLASSPATH /OneView
ENV AWS_SHARED_CREDENTIALS_FILE=/OneView/.aws/credentials
ENV AWS_DEFAULT_REGION=us-east-1

COPY ./Build/OneView/requirements.txt .
RUN pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt
RUN apt-get update && apt-get install -y openjdk-11-jre
ADD https://dbschema.com/jdbc-drivers/Db2JdbcDriver.zip .
RUN unzip ./Db2JdbcDriver.zip && rm ./Db2JdbcDriver.zip
RUN touch DB2JccConfiguration.properties
RUN echo "db2.jcc.charsetDecoderEncoder=3" >> ./DB2JccConfiguration.properties

COPY ./Script ./Script
COPY ./Build/Master ./Build/Master
COPY ./Build/OneView ./Build/OneView
COPY ./Source ./Source
RUN ./Script/bundle-project -i --directory ./ OneView

RUN rm -rf ./Script
RUN rm -rf ./Build
RUN rm -rf ./Source

# COPY ./Test/Python/ .

COPY ./Build/OneView/PPD/.env .
# COPY ./Build/OneView/credentials ${AWS_SHARED_CREDENTIALS_FILE}
