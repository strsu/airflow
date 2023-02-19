from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.models import Variable, TaskInstance
from airflow.utils.task_group import TaskGroup

from datetime import datetime, timedelta
from time import sleep

default_args = {
    "start_date": datetime(2023, 2, 19),
    "retries": 1,
    "catchup": False,
    "retry_delay": timedelta(minutes=1),
}


def dump() -> None:
    sleep(3)


def api(**context):
    task_instance = context["task_instance"]
    task_instance.xcom_push(key="resource_list", value=[1, 2, 3, 4])


def make_task(**context):
    res = context["task_instance"].xcom_pull(key="resource_list")


with DAG(
    dag_id="task_group",
    default_args=default_args,
    schedule_interval="0 */1 * * *",
    description="지하철 데이터 요청",
    tags=["task_group"],
) as dag:

    start = PythonOperator(task_id="api_call", python_callable=api)

    with TaskGroup(group_id="중개사") as CompanyGroup:
        result = [1, 2, 3, 4]
        for seq, r in enumerate(result):
            task = PythonOperator(task_id=f"task_{seq}", python_callable=dump)

            result2 = [1, 2, 3]
            task_list = []
            with TaskGroup(group_id=f"집합자원_{seq}") as AggGroup:
                for seq2, r in enumerate(result2):
                    task2 = PythonOperator(
                        task_id=f"Agg_{seq}_{seq2}", python_callable=dump
                    )
                    task_list.append(task2)

            task >> task_list

    end = PythonOperator(task_id="end", python_callable=dump)

    start >> CompanyGroup >> end
