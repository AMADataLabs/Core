FROM python:3.12.0a5-slim

ENV AIRFLOW_HOME=/home/airflow
ENV HOME=/Sync
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

COPY ./Build/Airflow/Sync/requirements.txt .
RUN pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt


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

RUN adduser --disabled-password --uid 1001 --gid 0 --home ${HOME} --no-create-home --gecos "Airflow" airflow

COPY ./Build/Airflow/entrypoint.sh entrypoint.sh
RUN chmod +x entrypoint.sh

# Save Git SSH key
COPY ./Build/Airflow/Sync/ssh_config.txt ssh_config
# RUN printenv GIT_SSH_KEY | sed 's/\\n/\n/g' > id_rsa
ENV GIT_SSH_COMMAND "ssh -o StrictHostKeyChecking=no -i ${HOME}/id_rsa"

# Bundle the app code
COPY ./Script ./Script
COPY ./Build/Master ./Build/Master
COPY ./Build/Airflow ./Build/Airflow
COPY ./Source ./Source

RUN ./Script/render-template \
    --template ./Build/Airflow/Sync/sync.env \
    --file ./.env \
    --vars pythonpath=${HOME}
RUN ./Script/bundle-project -i --directory ./ Airflow/Sync

RUN rm -rf ./Script
RUN rm -rf ./Build
RUN rm -rf ./Source

ENV PYTHONPATH ${HOME}

RUN chown -Rf 1001 ${HOME}
RUN chmod go+rwx ${HOME}

RUN mkdir -p ${AIRFLOW_HOME}/dags
RUN chown -Rf 1001 ${AIRFLOW_HOME}/dags
RUN chmod go+rwx ${AIRFLOW_HOME}/dags

USER 1001
