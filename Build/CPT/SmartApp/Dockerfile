# Build Example:
#    docker build -t cpt -f ./Build/CPT/Ingest/Dockerfile --build-arg --build-arg template_vars='user=bob,password=foo' ./
# Run Example:
#    docker run -e DOTENV_PATH=get_descriptors.env -ti cpt python -c "import awslambda; print(awslambda.handler(None, None))"

FROM python:3.9.5

ENV HOME /CPT
WORKDIR $HOME

# Install JDK 8
RUN apt update &&\
    apt install -y apt-transport-https software-properties-common &&\
    wget -qO - https://adoptopenjdk.jfrog.io/adoptopenjdk/api/gpg/key/public | apt-key add - &&\
    add-apt-repository --yes https://adoptopenjdk.jfrog.io/adoptopenjdk/deb/ &&\
    apt update &&\
    apt install -y adoptopenjdk-8-hotspot maven

# Build and install MarkLogic Content Pump command-line tool (mlcp)
RUN git clone --branch 10.0.6 https://github.com/marklogic/marklogic-contentpump.git &&\
    cd marklogic-contentpump &&\
    mvn clean package -DskipTests=true &&\
    cd $HOME &&\
    unzip marklogic-contentpump/deliverable/mlcp-10.0.6-bin.zip

ENV MLCP $HOME/mlcp-10.0.6/bin/mlcp.sh
