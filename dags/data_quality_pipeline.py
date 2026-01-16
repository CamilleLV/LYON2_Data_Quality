from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'data_engineer',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='sirene_data_quality_pipeline',
    default_args=default_args,
    start_date=datetime(2023, 1, 1),
    schedule_interval='@daily',
    catchup=False
) as dag:

    # Task 1: Ingest CSV -> MariaDB Raw
    ingest_task = BashOperator(
        task_id='ingest_data',
        bash_command='python /opt/airflow/scripts/ingest_data.py'
    )

    # Task 2: Clean Raw -> MariaDB Cleaned
    clean_task = BashOperator(
        task_id='clean_data',
        bash_command='python /opt/airflow/scripts/clean_data.py'
    )

    # Task 3: Validate Cleaned Data (Great Expectations)
    validate_task = BashOperator(
        task_id='validate_data',
        bash_command='python /opt/airflow/scripts/validate_data.py'
    )

    # Dependencies
    ingest_task >> clean_task >> validate_task