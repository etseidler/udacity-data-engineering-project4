/opt/airflow/start-services.sh
/opt/airflow/start.sh
airflow users create --email student@example.com --firstname aStudent --lastname aStudent --password XXXXX --role Admin --username XXXXX
airflow scheduler

# teardown
# ps au | grep airflow | awk '{print $2}' | xargs kill
