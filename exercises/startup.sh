/opt/airflow/start-services.sh
/opt/airflow/start.sh
airflow users create --email student@example.com --firstname aStudent --lastname aStudent --password XXXXX --role Admin --username XXXXX
/home/workspace/airflow/dags/cd0031-automate-data-pipelines/set_connections.sh
airflow scheduler

# teardown
# ps au | grep airflow | awk '{print $2}' | xargs kill
