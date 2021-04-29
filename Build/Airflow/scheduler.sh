#!/bin/bash

/usr/local/bin/airflow db init

/usr/local/bin/airflow users list | grep 'DataLabs@ama-assn.org'
if [[ $? != 0 ]]; then
    /usr/local/bin/airflow users create \
        --username datalabs\
        --firstname Data \
        --lastname Labs \
        --role Admin \
        --email DataLabs@ama-assn.org \
        --password CHANGEME
fi

/usr/local/bin/airflow scheduler
