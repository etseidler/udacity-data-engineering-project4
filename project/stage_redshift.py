from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator, Variable
from airflow.secrets.metastore import MetastoreBackend
from airflow.utils.decorators import apply_defaults

class StageToRedshiftOperator(BaseOperator):
    ui_color = '#358140'
    template_fields = ("s3_key",)
    copy_sql = """
        COPY {}
        FROM '{}'
        ACCESS_KEY_ID '{}'
        SECRET_ACCESS_KEY '{}'
        JSON {}
    """

    @apply_defaults
    def __init__(self,
                 redshift_conn_id="redshift",
                 aws_credentials_id='aws_credentials',
                 table="",
                 s3_bucket="eric-seidler-airflow",
                 s3_key="",
                 json="'auto'",
                 *args, **kwargs):
        execution_date = kwargs['execution_date']
        ds = kwargs['ds']

        super(StageToRedshiftOperator, self).__init__(*args, **kwargs)
        self.table = table
        self.redshift_conn_id = redshift_conn_id
        self.s3_bucket = s3_bucket
        self.s3_key = f"{s3_key}/{execution_date.year}/{execution_date.month}/{ds}-events.json"
        self.aws_credentials_id = aws_credentials_id
        self.json = json

    def execute(self, context):
        metastoreBackend = MetastoreBackend()
        aws_connection=metastoreBackend.get_connection(self.aws_credentials_id)
        redshift = PostgresHook(postgres_conn_id=self.redshift_conn_id)

        self.log.info("Clearing data from destination Redshift table")
        redshift.run("DELETE FROM {}".format(self.table))

        self.log.info("Copying data from S3 to Redshift")
        rendered_key = self.s3_key.format(**context)
        s3_path = "s3://{}/{}".format(self.s3_bucket, rendered_key)
        formatted_sql = StageToRedshiftOperator.copy_sql.format(
            self.table,
            s3_path,
            aws_connection.login,
            aws_connection.password,
            self.json
        )
        redshift.run(formatted_sql)





