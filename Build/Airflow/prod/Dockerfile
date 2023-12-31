FROM python:3.12.0a5-slim

# ARG AIRFLOW_VERSION=1.10.14
ARG AIRFLOW_VERSION=2.1.0

ENV AIRFLOW_HOME=/home/airflow
ENV SLUGIFY_USES_TEXT_UNIDECODE=yes
ENV USER=airflow USER_ID=1001

RUN useradd -ms /bin/bash -d ${AIRFLOW_HOME} --uid ${USER_ID} -G 0 airflow

RUN pip install --upgrade pip==20.2.4

RUN pip install --no-cache-dir apache-airflow['crypto','kubernetes','postgres']==${AIRFLOW_VERSION} \
    --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-3.7.txt"

WORKDIR ${AIRFLOW_HOME}

COPY Build/Airflow/scheduler.sh .
RUN chmod gu+rwx scheduler.sh

COPY Build/Airflow/webserver.sh .
RUN chmod gu+rwx webserver.sh

RUN mkdir -p shared \
    && ln -s shared dags \
    && ln -s shared logs

COPY Build/Airflow/Worker/prod/pod.yaml ./worker.yaml

RUN chown -R airflow:0 ${AIRFLOW_HOME} && chmod -R 777 ${AIRFLOW_HOME}

USER ${USER_ID}
