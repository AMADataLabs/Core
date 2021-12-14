# Build Example:
# docker build -t license-movement -f ./Build/LicenseMovement/Dockerfile --build-arg template_vars='key=KEY,secret=SECRET,AIMS_PASSWORD=PSSWD' ./

FROM python:3.7
ENV PYTHONPATH=/LicenseMovement:/LicenseMovement/site-packages
RUN echo "hadi_test"
ENV JAVA_HOME /usr/lib/jvm/java-1.11.0-openjdk-amd64
ENV CLASSPATH=/AMC:$JAVA_HOME/lib/dt.jar:$JAVA_HOME/lib/tools.jar
ENV HOME=/LicenseMovement
WORKDIR $HOME


# Required for pyodbc
RUN apt-get update && apt-get install -y --no-install-recommends \
    unixodbc-dev \
    unixodbc

COPY ./Build/LicenseMovement/requirements.txt .
RUN pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt

COPY ./Script ./Script
COPY ./Build/Master ./Build/Master
COPY ./Build/LicenseMovement ./Build/LicenseMovement
COPY ./Source ./Source

RUN ./Script/bundle-project -i --directory ./ LicenseMovement

ARG template_vars
RUN echo $template_vars
COPY ./Build/LicenseMovement/*.env.jinja ./

RUN find ./ -name "*.env.jinja" -exec \
   ./Script/render-template \
    --template {} \
    --file {} \
   --vars pythonpath=/LicenseMovement,$template_vars \;
RUN echo "hadi_test"
RUN ./Script/bundle-project -i --directory ./ LicenseMovement

RUN apt-get update && apt-get install -y openjdk-11-jre
# ADD https://dbschema.com/jdbc-drivers/SqlServerJdbcDriver.zip .
# RUN unzip ./SqlServerJdbcDriver.zip && rm ./SqlServerJdbcDriver.zip
# ADD https://dbschema.com/jdbc-drivers/Db2JdbcDriver.zip .
# RUN unzip ./Db2JdbcDriver.zip && rm ./Db2JdbcDriver.zip
# RUN echo "db2.jcc.charsetDecoderEncoder=3" >> ./DB2JccConfiguration.properties
ADD https://dbschema.com/jdbc-drivers/InformixJdbcDriver.zip .
RUN unzip ./InformixJdbcDriver.zip && rm ./InformixJdbcDriver.zip