FROM python:3.7

ARG AIRFLOW_VERSION=1.10.11

ENV AIRFLOW_HOME=/airflow
ENV SLUGIFY_USES_TEXT_UNIDECODE=yes
ENV USER=airflow USER_ID=1001

RUN useradd -ms /bin/bash -d ${AIRFLOW_HOME} --uid ${USER_ID} -G 0 airflow

RUN pip install --no-cache-dir apache-airflow['crypto','kubernetes','postgres']==${AIRFLOW_VERSION}

COPY Build/Airflow/scheduler.sh ${AIRFLOW_HOME}/scheduler.sh
RUN chmod gu+rwx ${AIRFLOW_HOME}/scheduler.sh

COPY Build/Airflow/webserver.sh ${AIRFLOW_HOME}/webserver.sh
RUN chmod gu+rwx ${AIRFLOW_HOME}/webserver.sh

RUN chown -R airflow:0 ${AIRFLOW_HOME} && chmod -R g+rwx,o-w ${AIRFLOW_HOME}

USER ${USER_ID}
WORKDIR ${AIRFLOW_HOME}
