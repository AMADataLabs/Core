# Build Example:
#    docker build -t one-view -f ./Build/OneView/Dockerfile --build-arg template_vars='user=bob,password=foo' ./
# Run Example:
#    docker run -ti one-view -e DOTENV_PATH=ppd.env python -c "import awslambda; print(awslambda.handler(None, None))"

FROM python:3.7
ENV PYTHONPATH=/ContactID:/ContactID/site-packages
ENV CLASSPATH=/ContactID
#ENV AWS_SHARED_CREDENTIALS_FILE=/ContactID/.aws/credentials
ENV AWS_DEFAULT_REGION=us-east-1
ENV HOME=/ContactID
WORKDIR $HOME

COPY ./Build/ContactID/requirements.txt .
RUN cat requirements.txt | grep pip== > pip-requirements.txt &&\
    pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r pip-requirements.txt &&\
    pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt

RUN apt-get update && apt-get install -y openjdk-11-jre
ADD https://dbschema.com/jdbc-drivers/Db2JdbcDriver.zip .
RUN unzip ./Db2JdbcDriver.zip && rm ./Db2JdbcDriver.zip
RUN echo "db2.jcc.charsetDecoderEncoder=3" >> ./DB2JccConfiguration.properties

COPY ./Script ./Script
COPY ./Build/Master ./Build/Master
COPY ./Build/ContactID ./Build/ContactID
COPY ./Source ./Source
COPY ./Build/ContactID/known_hosts $HOME/.ssh/known_hosts

ARG template_vars
RUN echo $template_vars
COPY ./Build/ContactID/*.env ./

RUN find ./ -name "*.env" -exec \
   ./Script/render-template \
    --template {} \
    --file {} \
   --vars pythonpath=/ContactID,$template_vars \;
RUN ./Script/bundle-project -i --directory ./ ContactID

RUN mkdir -p /root/.ssh
RUN echo "eft.ama-assn.org,10.195.141.136 ssh-rsa AAAAB3NzaC1yc2EAAAABEQAAAQEAqQX4RaqXGy0/QjCSPrDVrmY8jMKwXXVEvD0iB8Q2q8DE/X5wqTuFR2Dg6KZygUo7IERLMMUVYTzsnDwHF/3kXNFtBtB0oOuV81LNSXe7afKBUzmOwHwAWhM99MXrb6R7bQ9XgefXYxGtFlpaPoBGrOs0+YUFiSYAVsl5EBe5QVpY4myfX9aBpjzHcwFXviviC9ytJNunhVxi2WL3ebk3fCkf0XcKPc+pbWfhUzERPuWhHnjDyYI5/GStMdIaGs5i5OYboMQJC60DDhECeHnjuo5MvNxq7P4W+pEUZUuj85z7Kf3SseFy7j1q34sTEn1UsVKimv1BP32f+6vv08m6tw==" > /root/.ssh/known_hosts

RUN rm -rf ./Script
RUN rm -rf ./Build
RUN rm -rf ./Source
