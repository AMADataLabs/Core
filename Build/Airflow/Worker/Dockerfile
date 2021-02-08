FROM python:3.7

ARG AIRFLOW_VERSION=2.0.0

ENV HOME /home/airflow
ENV SLUGIFY_USES_TEXT_UNIDECODE=yes
ENV USER=airflow
ENV USER_ID=1000280000

# RUN useradd -ms /bin/bash -d ${HOME} --uid ${USER_ID} -G 0 airflow

RUN pip install --no-cache-dir apache-airflow['crypto','kubernetes','postgres']==${AIRFLOW_VERSION} \
    --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-3.8.txt"

# FROM apache/airflow:1.10.12

# USER root

WORKDIR ${HOME}

# Python binary and source dependencies
RUN apt-get update -qq && \
 DEBIAN_FRONTEND=noninteractive apt-get install -yq --no-install-recommends \
 tini \
 build-essential \
 ca-certificates \
 cmake \
 curl \
 git \
 make \
 locales \
 locales-all \
 libcurl4-openssl-dev \
 libffi-dev \
 libsqlite3-dev \
 libzmq3-dev \
 pandoc \
 sqlite3 \
 texlive-fonts-recommended \
 texlive-latex-base \
 texlive-latex-extra \
 zlib1g-dev && \
 apt-get clean && \
 rm -rf /var/lib/apt/lists/*

ENV LC_ALL en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US.UTF-8

# Install nss_wrapper.
RUN curl -SL -o nss_wrapper.tar.gz https://ftp.samba.org/pub/cwrap/nss_wrapper-1.1.2.tar.gz && \
 mkdir nss_wrapper && \
 tar -xC nss_wrapper --strip-components=1 -f nss_wrapper.tar.gz && \
 rm nss_wrapper.tar.gz && \
 mkdir nss_wrapper/obj && \
 (cd nss_wrapper/obj && \
 cmake -DCMAKE_INSTALL_PREFIX=/usr/local -DLIB_SUFFIX=64 .. && \
 make && \
 make install) && \
 rm -rf nss_wrapper

COPY ./Build/Airflow/entrypoint.sh ${HOME}/entrypoint.sh
RUN chmod +x ${HOME}/entrypoint.sh

ENV PYTHONPATH ${HOME}
ENV CLASSPATH=${HOME}

RUN apt-get update && apt-get install -y openjdk-11-jre
ADD https://dbschema.com/jdbc-drivers/Db2JdbcDriver.zip .
RUN unzip ./Db2JdbcDriver.zip && rm ./Db2JdbcDriver.zip
RUN echo "db2.jcc.charsetDecoderEncoder=3" >> ./DB2JccConfiguration.properties
ADD https://dbschema.com/jdbc-drivers/InformixJdbcDriver.zip .
RUN unzip ./InformixJdbcDriver.zip && rm ./InformixJdbcDriver.zip

COPY ./Build/OneView/requirements.txt .
RUN pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt

COPY ./Source/Python/datalabs datalabs
COPY ./Source/Python/neptune_python_utils neptune_python_utils

# ENV DAG_SOURCE_PATH ${HOME}/datalabs/airflow/dag
# ENV DAG_TARGET_PATH ${HOME}/dags

RUN chown -Rf ${USER_ID} ${HOME}
RUN chmod go+rwx ${HOME}
RUN echo "runner:x:${USER_ID}:0:Airflow,,,:/home/airflow:/usr/sbin/nologin" >> /etc/passwd

USER ${USER_ID}
ENTRYPOINT ["/home/airflow/entrypoint.sh"]
