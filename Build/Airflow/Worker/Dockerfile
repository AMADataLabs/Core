FROM python:3.9.5

ARG AIRFLOW_VERSION=2.1.0

ENV HOME /home/airflow
ENV SLUGIFY_USES_TEXT_UNIDECODE=yes
ENV USER=airflow
ENV USER_ID=1001

WORKDIR ${HOME}

RUN pip install --no-cache-dir apache-airflow['crypto','kubernetes','postgres']==${AIRFLOW_VERSION} \
    --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-3.7.txt"

RUN chown -Rf ${USER_ID} ${HOME}
RUN chmod go+rwx ${HOME}

USER ${USER_ID}
