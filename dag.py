import airflow
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.dummy_operator import DummyOperator
from datetime import timedelta
from airflow.utils.trigger_rule import TriggerRule

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': airflow.utils.dates.days_ago(0),
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'Bash_test',
    default_args=default_args,
    description='A simple DAG with bash_operator',
    schedule_interval='0 */5 * * *')

templated_command = """
{% for i in range(5) %}
    echo $i
    echo "{{ params.my_param }}"
{% endfor %}
"""

t1 = BashOperator(
    task_id='templated',
    depends_on_past=False,
    bash_command=templated_command,
    params={'my_param': 'Parameter I passed in'},
    dag=dag)


t2 = BashOperator(
    task_id='sleep',
    depends_on_past=False,
    bash_command='sleep 5',
    dag=dag)

t3 = BashOperator(
    task_id='print_some',
    bash_command='echo "Hello iam task#3"',
    dag=dag)

t2.set_upstream(t1)
t3.set_upstream(t1)

templ = """
    sleep 10
    echo "ready for final"
"""

t4 = BashOperator(
    task_id='wait_print',
    bash_command=templ,
    dag=dag
)

t4.set_upstream(t3)

t5 = DummyOperator(
    task_id='t5',
    dag=dag
)

t5.set_upstream(t3)

tfinal = BashOperator(
    task_id='final',
    bash_command='echo "All tasks done"',
    trigger_rule=TriggerRule.ALL_DONE,
    dag=dag
)

tfinal.set_upstream([t4, t5])
