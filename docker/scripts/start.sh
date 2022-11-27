#!/usr/bin/env bash

rm *.pid

airflow db init

airflow users create \
    --role Admin \
    --username admin \
    --email admin \
    --firstname admin \
    --lastname admin \
    --password admin

airflow db upgrade

nohup airflow webserver -p 8080 &
nohup airflow scheduler &
nohup airflow celery worker