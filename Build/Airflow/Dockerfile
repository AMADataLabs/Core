FROM python:3.7

ARG AIRFLOW_VERSION=1.10.12

ENV AIRFLOW_HOME=/airflow
ENV SLUGIFY_USES_TEXT_UNIDECODE=yes
ENV USER=airflow USER_ID=1001

RUN useradd -ms /bin/bash -d ${AIRFLOW_HOME} --uid ${USER_ID} -G 0 airflow

RUN pip install --no-cache-dir apache-airflow['crypto','kubernetes','postgres']==${AIRFLOW_VERSION} \
    --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-1.10.12/constraints-3.8.txt"

WORKDIR ${AIRFLOW_HOME}

COPY Build/Airflow/scheduler.sh .
RUN chmod gu+rwx scheduler.sh

COPY Build/Airflow/webserver.sh .
RUN chmod gu+rwx webserver.sh

RUN mkdir -p shared \
    && ln -s shared dags \
    && ln -s shared logs

RUN chown -R airflow:0 ${AIRFLOW_HOME} && chmod -R g+rws,o-w ${AIRFLOW_HOME}

USER ${USER_ID}
