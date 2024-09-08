import datetime as dt
import os
import sys

from airflow.models import DAG
from airflow.operators.python import PythonOperator


path = '/opt/airflow'
# Добавим путь к коду проекта в переменную окружения, чтобы он был доступен python-процессу
os.environ['PROJECT_PATH'] = path
# Добавим путь к коду проекта в $PATH, чтобы импортировать функции
sys.path.insert(0, path)

from modules.pipeline import pipeline
from parsers.alpha import main_alpha
from parsers.autogpbl import main_gpbl
from parsers.europlan import main_europlan


args = {
    'owner': 'airflow',
    'start_date': dt.datetime(2024, 9, 1),
    'retries': 1,
    'retry_delay': dt.timedelta(minutes=1),
    'depends_on_past': False,
}

with DAG(
        dag_id='car_price_prediction',
        schedule_interval="00 00 * * 0",
        default_args=args,
) as dag:
    alpha = PythonOperator(
        task_id='alpha',
        python_callable=main_alpha,
        dag=dag
    )

    europlan = PythonOperator(
        task_id='europlan',
        python_callable=main_europlan,
        dag=dag
    )

    autogpbl = PythonOperator(
        task_id='autogpbl',
        python_callable=main_gpbl,
        dag=dag
    )

    pipeline = PythonOperator(
        task_id='pipeline',
        python_callable=pipeline,
        dag=dag
    )

    alpha >> europlan >> autogpbl >> pipeline

