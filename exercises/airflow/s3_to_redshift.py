import pendulum
import logging

from airflow.decorators import dag, task
from airflow.secrets.metastore import MetastoreBackend
from airflow.hooks.postgres_hook import PostgresHook
from airflow.operators.postgres_operator import PostgresOperator


# Use the PostgresHook to create a connection using the Redshift credentials from Airflow
# Use the PostgresOperator to create the Trips table
# Use the PostgresOperator to run the LOCATION_TRAFFIC_SQL


from exercises import sql_statements

@dag(
    start_date=pendulum.now()
)
def load_data_to_redshift():

    @task
    def load_task():
        metastoreBackend = MetastoreBackend()
        aws_connection=metastoreBackend.get_connection("aws_credentials")
        logging.info(vars(aws_connection))
        ## commented because during first run,
        ## create_table succeeded, but location_traffic_task failed
        # redshift_hook = PostgresHook("redshift")
        # redshift_hook.run(sql_statements.COPY_ALL_TRIPS_SQL.format(aws_connection.login, aws_connection.password))

    @task()
    def check_greater_than_zero(*args, **kwargs):
        table = kwargs["params"]["table"]
        redshift_hook = PostgresHook("redshift")
        records = redshift_hook.get_records(f"SELECT COUNT(*) FROM {table}")
        if len(records) < 1 or len(records[0]) < 1:
            raise ValueError(f"Data quality check failed. {table} returned no results")
        num_records = records[0][0]
        if num_records < 1:
            raise ValueError(f"Data quality check failed. {table} contained 0 rows")
        logging.info(f"Data quality on table {table} check passed with {records[0][0]} records")

    create_table_task=PostgresOperator(
        task_id="create_table",
        postgres_conn_id="redshift",
        sql=sql_statements.CREATE_TRIPS_TABLE_SQL
    )

    # needs to be split up to work per https://knowledge.udacity.com/questions/989716
    # location_traffic_task = PostgresOperator(
    #     task_id="calculate_location_traffic",
    #     postgres_conn_id="redshift",
    #     sql=sql_statements.LOCATION_TRAFFIC_SQL
    # )
    begin_transaction = PostgresOperator(
        task_id='begin_transaction',
        postgres_conn_id='redshift',
        sql='BEGIN;'
    )

    drop_table = PostgresOperator(
        task_id='drop_table',
        postgres_conn_id='redshift',
        sql='DROP TABLE IF EXISTS station_traffic;'
    )

    create_and_insert_into_table = PostgresOperator(
        task_id='create_and_insert_into_table',
        postgres_conn_id='redshift',
        sql="""
        CREATE TABLE station_traffic AS
        SELECT
            DISTINCT(t.from_station_id) AS station_id,
            t.from_station_name AS station_name,
            num_departures,
            num_arrivals
        FROM trips t
        JOIN (
            SELECT
                from_station_id,
                COUNT(from_station_id) AS num_departures
            FROM trips
            GROUP BY from_station_id
        ) AS fs ON t.from_station_id = fs.from_station_id
        JOIN (
            SELECT
                to_station_id,
                COUNT(to_station_id) AS num_arrivals
            FROM trips
            GROUP BY to_station_id
        ) AS ts ON t.from_station_id = ts.to_station_id;
        """
    )

    load_data = load_task()
    check_trips_task = check_greater_than_zero(
        params={
            'table':'trips'
        }
    )

    check_stations_task = check_greater_than_zero(
        params={
            'table': 'stations',
        }
    )

    ## commented because during first run,
    ## create_table succeeded, but location_traffic_task failed
    # create_table_task >> load_data
    # load_data >> check_trips_task
    load_data >> begin_transaction
    begin_transaction >> drop_table
    drop_table >> create_and_insert_into_table
    create_and_insert_into_table >> check_stations_task



s3_to_redshift_dag = load_data_to_redshift()
