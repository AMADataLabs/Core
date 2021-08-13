# Build Example:
#    docker build -t oneview-etl -f ./Build/OneView/ETL/Dockerfile --build-arg template_vars='user=bob,password=foo' ./
# Run Example:
#    docker run -e DOTENV_PATH=physician.env --rm -p 9000:8080 oneview-etl
#    curl -XPOST "http://192.168.99.105:9000/2015-03-31/functions/function/invocations" -d '{}'

FROM public.ecr.aws/lambda/python:3.7

WORKDIR /OneView
ENV PYTHONPATH=/OneView:/OneView/site-packages
ENV CLASSPATH=/OneView
ENV AWS_DEFAULT_REGION=us-east-1

COPY ./Build/OneView/alembic/versions .

COPY ./Build/OneView/requirements.txt .
RUN chown -R root:root /var/lang/lib/python3.7
RUN pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt

COPY ./Script ./Script
COPY ./Build/Master ./Build/Master
COPY ./Build/OneView ./Build/OneView
COPY ./Source/Python ./Source/Python
COPY ./Source/Bash ./Source/Bash
COPY ./Deploy/OneView/upgrade-database .

ARG template_vars
RUN echo $template_vars
COPY ./Build/OneView/*.env ./
RUN find ./ -name "*.env" -exec \
    ./Script/render-template \
    --template {} \
    --file {} \
    --vars pythonpath=/OneView,$template_vars \;
RUN ./Script/bundle-project -i --directory ./ OneView

RUN rm -rf ./Build/Master
RUN rm -rf ./Source

COPY ./Build/OneView/lambda-entrypoint.sh /
RUN chmod a+x /lambda-entrypoint.sh

ADD https://dbschema.com/jdbc-drivers/Db2JdbcDriver.zip .
RUN unzip ./Db2JdbcDriver.zip && rm ./Db2JdbcDriver.zip
RUN echo "db2.jcc.charsetDecoderEncoder=3" >> ./DB2JccConfiguration.properties
ADD https://dbschema.com/jdbc-drivers/InformixJdbcDriver.zip .
RUN unzip ./InformixJdbcDriver.zip && rm ./InformixJdbcDriver.zip

CMD ["awslambda.handler"]
