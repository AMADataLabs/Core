FROM python:3.7

ARG AIRFLOW_VERSION=1.10.11

ENV AIRFLOW_HOME=/airflow
ENV SLUGIFY_USES_TEXT_UNIDECODE=yes
ENV USER=airflow USER_ID=1001

WORKDIR ${AIRFLOW_HOME}

RUN useradd -ms /bin/bash -d ${AIRFLOW_HOME} --uid ${USER_ID} airflow
RUN pip install --no-cache-dir apache-airflow['crypto','kubernetes','postgres']==${AIRFLOW_VERSION}
RUN chown -R airflow: ${AIRFLOW_HOME}

USER ${USER_ID}
