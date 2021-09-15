# Build Example:
#    docker build -t addressload -f ./Build/AddressLoad/Dockerfile --build-arg template_vars='EFT_PASSWORD=pass' ./
# Run Example:
#    docker run -e DOTENV_PATH=aggregate.env -ti addressload python task.py

FROM python:3.7
ENV PYTHONPATH=/AddressLoad:/AddressLoad/site-packages
ENV CLASSPATH=/AddressLoad
ENV HOME=/AddressLoad
WORKDIR $HOME

COPY ./Build/AddressLoad/requirements.txt .
RUN cat requirements.txt | grep pip== > pip-requirements.txt &&\
    pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r pip-requirements.txt &&\
    pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt

# RUN apt-get update && apt-get install -y openjdk-11-jre
# ADD https://dbschema.com/jdbc-drivers/Db2JdbcDriver.zip .
# RUN unzip ./Db2JdbcDriver.zip && rm ./Db2JdbcDriver.zip
# RUN echo "db2.jcc.charsetDecoderEncoder=3" >> ./DB2JccConfiguration.properties
# ADD https://dbschema.com/jdbc-drivers/InformixJdbcDriver.zip .
# RUN unzip ./InformixJdbcDriver.zip && rm ./InformixJdbcDriver.zip

COPY ./Script ./Script
COPY ./Build/Master ./Build/Master
COPY ./Build/AddressLoad ./Build/AddressLoad
COPY ./Source ./Source
# COPY ./Build/AddressLoad/known_hosts $HOME/.ssh/known_hosts

ARG template_vars
RUN echo $template_vars
COPY ./Build/AddressLoad/*.env.jinja ./

RUN find ./ -name "*.env.jinja" | sed 's/.jinja//' | xargs -t -I {}\
    ./Script/render-template \
    --template {}.jinja \
    --file {} \
    --vars pythonpath=/AddressLoad,$template_vars
RUN ./Script/bundle-project -i --directory ./ AddressLoad

RUN rm -rf ./Script
RUN rm -rf ./Build
RUN rm -rf ./Source
