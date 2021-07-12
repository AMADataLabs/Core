# Build Example:
#    docker build -t amc -f ./Build/AMC/Dockerfile --build-arg template_vars='user=bob,password=foo' ./
# Run Example:
#    docker run -e DOTENV_PATH=flagged_addresses_report.env -ti amc python task.py

FROM python:3.7
ENV PYTHONPATH=/AMC:/AMC/site-packages
ENV CLASSPATH=/AMC
#ENV AWS_SHARED_CREDENTIALS_FILE=/AMC/.aws/credentials
ENV AWS_DEFAULT_REGION=us-east-1
ENV HOME=/AMC
WORKDIR $HOME

COPY ./Build/AMC/requirements.txt .
RUN cat requirements.txt | grep pip== > pip-requirements.txt &&\
    pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r pip-requirements.txt &&\
    pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt

RUN apt-get update && apt-get install -y openjdk-11-jre
ADD https://dbschema.com/jdbc-drivers/Db2JdbcDriver.zip .
RUN unzip ./Db2JdbcDriver.zip && rm ./Db2JdbcDriver.zip
RUN echo "db2.jcc.charsetDecoderEncoder=3" >> ./DB2JccConfiguration.properties

COPY ./Script ./Script
COPY ./Build/Master ./Build/Master
COPY ./Build/AMC ./Build/AMC
COPY ./Source ./Source
COPY ./Build/AMC/known_hosts $HOME/.ssh/known_hosts

ARG template_vars
RUN echo $template_vars
COPY ./Build/AMC/*.env ./

RUN find ./ -name "*.env.jinja" -exec \
   ./Script/render-template \
    --template {} \
    --file $(echo {} | sed 's/.jinja//') \
   --vars pythonpath=/AMC,$template_vars \;
RUN ./Script/bundle-project -i --directory ./ AMC

RUN rm -rf ./Script
RUN rm -rf ./Build
RUN rm -rf ./Source
