from kafka import KafkaProducer
from datetime import datetime, timedelta
import arrow
import requests
import urllib3
import json

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.models import Variable

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


ENV = Variable.get("env")
if not isinstance(ENV, dict):
    ENV = eval(ENV)


def on_send_success(record_metadata):
    print("topic", record_metadata.topic)
    print("partition", record_metadata.partition)
    print("offset", record_metadata.offset)


def on_send_error(excp):
    print("I am an errback", exc_info=excp)
    # handle exception


def get_subway(**kwargs):
    execute_date = (
        arrow.get(kwargs["next_date"])
        .to("Asia/Seoul")
        .shift(days=-4)
        .format("YYYYMMDD")
    )

    start_page = 0
    end_page = 999
    subway_info = []

    producer = KafkaProducer(
        acks=1,
        compression_type="gzip",
        bootstrap_servers=["192.168.209.1:9092"],
        value_serializer=lambda x: json.dumps(x).encode("utf-8"),
    )

    while True:
        url = f"http://openapi.seoul.go.kr:8088/{ENV.get('api')}/json/CardSubwayStatsNew/{start_page}/{end_page}/{execute_date}"

        response = requests.get(url)

        res_json = response.json()
        if "CardSubwayStatsNew" not in res_json:
            print(f"{execute_date} 날짜에 해당하는 데이터가 없습니다.")
            break

        res_json = res_json["CardSubwayStatsNew"]
        if res_json["RESULT"]["CODE"] == "INFO-200":
            break

        subway_info.extend(res_json["row"])
        start_page += 1000
        end_page += 1000

    data = {"Airflow": f"subway - {execute_date}"}
    producer.send("topic", value=data).add_callback(on_send_success).add_errback(
        on_send_error
    )
    producer.flush()  # block until all async messages are sent


default_args = {
    "start_date": datetime(2022, 11, 23),
    "retries": 1,
    "catchup": False,
    "retry_delay": timedelta(minutes=1),
}

with DAG(
    dag_id="get_subway",
    default_args=default_args,
    schedule_interval="0 16 */1 * *",
    description="지하철 데이터 요청",
    tags=["get_subway"],
) as dag:
    task = PythonOperator(
        task_id="calc",
        python_callable=get_subway,
        op_kwargs={
            "next_date": "{{ next_execution_date }}",
        },
    )

    task
