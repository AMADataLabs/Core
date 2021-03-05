# Build Example:
#    docker build -t one-view -f ./Build/OneView/Dockerfile --build-arg template_vars='user=bob,password=foo' ./
# Run Example:
#    docker run -ti one-view -e DOTENV_PATH=ppd.env python -c "import awslambda; print(awslambda.handler(None, None))"

FROM python:3.7
WORKDIR /OneView
ENV PYTHONPATH=/OneView:/OneView/site-packages
ENV CLASSPATH=/OneView
ENV AWS_DEFAULT_REGION=us-east-1

COPY ./Build/OneView/requirements.txt .
RUN pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt

RUN apt-get update && apt-get install -y openjdk-11-jre
ADD https://dbschema.com/jdbc-drivers/Db2JdbcDriver.zip .
RUN unzip ./Db2JdbcDriver.zip && rm ./Db2JdbcDriver.zip
RUN echo "db2.jcc.charsetDecoderEncoder=3" >> ./DB2JccConfiguration.properties
ADD https://dbschema.com/jdbc-drivers/InformixJdbcDriver.zip .
RUN unzip ./InformixJdbcDriver.zip && rm ./InformixJdbcDriver.zip

COPY ./Script ./Script
COPY ./Build/Master ./Build/Master
COPY ./Build/OneView ./Build/OneView
COPY ./Source ./Source

ARG template_vars
RUN echo $template_vars
COPY ./Build/OneView/*.env ./
RUN find ./ -name "*.env" -exec \
    ./Script/render-template \
    --template {} \
    --file {} \
    --vars pythonpath=/OneView,$template_vars \;
RUN ./Script/bundle-project -i --directory ./ OneView

RUN rm -rf ./Script
RUN rm -rf ./Build
RUN rm -rf ./Source
