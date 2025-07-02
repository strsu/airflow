"""
Simple ETL DAG example with TaskGroups for Airflow 3.0
"""
from datetime import datetime, timedelta
import json
import logging
import random
import requests
import time

from airflow import DAG
from airflow.decorators import task, task_group
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator
from airflow.operators.bash import BashOperator

# DAG 기본 설정
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

# DAG 정의
with DAG(
    'example_etl_pipeline',
    default_args=default_args,
    description='예제 ETL 파이프라인',
    schedule='@daily',
    start_date=datetime.now() - timedelta(days=1),
    catchup=False,
    tags=['example', 'etl'],
) as dag:
    
    start = EmptyOperator(
        task_id='start',
    )

    # 데이터 추출 함수
    @task(task_id="extract_data")
    def extract(**kwargs):
        """예시 데이터를 추출하는 함수"""
        # 실제로는 데이터베이스나 API에서 데이터를 가져올 것
        logging.info("데이터 추출 중...")
        
        # 예시 데이터 생성
        data = []
        for i in range(10):
            data.append({
                "id": i,
                "value": random.randint(1, 100),
                "timestamp": datetime.now().isoformat()
            })
        
        # XCom을 통해 다음 태스크로 데이터 전달
        logging.info(f"추출된 데이터 개수: {len(data)}")
        return data

    # 각 변환 작업을 별도의 태스크로 정의
    @task(task_id="transform_values")
    def transform_values(data):
        """값 변환 처리"""
        logging.info("데이터 값 변환 중...")
        transformed_data = []
        for item in data:
            transformed_item = item.copy()
            transformed_item["value"] = item["value"] * 2
            transformed_data.append(transformed_item)
        return transformed_data
    
    @task(task_id="filter_data")
    def filter_data(data):
        """데이터 필터링"""
        logging.info("데이터 필터링 중...")
        filtered = [item for item in data if item["value"] > 50]
        logging.info(f"필터링 후 데이터 개수: {len(filtered)}")
        return filtered
    
    @task(task_id="enrich_data")
    def enrich_data(data):
        """데이터 보강"""
        logging.info("데이터 보강 중...")
        enriched_data = []
        for item in data:
            enriched_item = item.copy()
            enriched_item["status"] = "active" if item["value"] > 75 else "inactive"
            enriched_data.append(enriched_item)
        return enriched_data
    
    # 데이터 적재 태스크
    @task(task_id="load_data")
    def load(data):
        """처리된 데이터를 저장하는 함수"""
        logging.info(f"최종 데이터 {len(data)}개 저장 중...")
        
        # 실제로는 데이터베이스에 저장
        for item in data:
            logging.info(f"데이터 저장: {item}")
        
        return {"status": "success", "count": len(data)}
    
    # 태스크 실행 보고
    def report_status(**context):
        ti = context['ti']
        result = ti.xcom_pull(task_ids='load_data')
        logging.info(f"ETL 파이프라인 완료 - 상태: {result['status']}, 처리 건수: {result['count']}")

    report = PythonOperator(
        task_id='report_status',
        python_callable=report_status,
    )
    
    # 외부 API 호출 예시 (실제로는 실행되지 않음)
    check_api = BashOperator(
        task_id='check_api',
        bash_command='echo "API 상태 확인: OK"',
    )
    
    end = EmptyOperator(
        task_id='end',
    )
    
    # 태스크 의존성과 데이터 흐름을 명시적으로 설정
    extracted_data = extract()
    transformed_data = transform_values(extracted_data)
    filtered_data = filter_data(transformed_data)
    enriched_data = enrich_data(filtered_data)
    loaded_result = load(enriched_data)
    
    # 전체 워크플로우 정의
    start >> extracted_data >> transformed_data >> filtered_data >> enriched_data >> loaded_result >> report >> check_api >> end
