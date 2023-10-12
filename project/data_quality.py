from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults

class DataQualityOperator(BaseOperator):

    ui_color = '#89DA59'

    @apply_defaults
    def __init__(self,
                 redshift_conn_id="redshift",
                 tables=[],
                 quality_check_sql = 'SELECT COUNT(*) FROM {}',
                 expected_min_rows=1,
                 *args, **kwargs):

        super(DataQualityOperator, self).__init__(*args, **kwargs)
        self.redshift_conn_id = redshift_conn_id
        self.tables = tables
        self.quality_check_sql = quality_check_sql
        self.expected_min_rows = expected_min_rows

    def execute(self, context):
        if not self.tables:
            self.log.info("No input tables provided. Skipping quality checks.")

        for table in self.tables:
            redshift = PostgresHook(postgres_conn_id=self.redshift_conn_id)
            formatted_sql = self.quality_check_sql.format(table)
            records = redshift.get_records(formatted_sql)
            if len(records) < self.expected_min_rows or len(records[0]) < self.expected_min_rows:
                raise ValueError(f"Data quality check failed. {table} returned no results")
            num_records = records[0][0]
            if num_records < self.expected_min_rows:
                raise ValueError(f"Data quality check failed. {table} contained 0 rows")
            self.log.info(f"Data quality on table {table} check passed with {records[0][0]} records")