#!/bin/bash
airflow connections add aws_credentials --conn-uri '<AWS_CREDENTIALS_CONNECTION>'
airflow connections add redshift --conn-uri 'redshift://<AWS_USER>:<AWS_REDSHIFT_PW>@<AWS_REDSHIFT_URL>:5439/dev'
airflow variables set s3_bucket <S3_BUCKET_NAME>
airflow variables set s3_prefix data-pipelines
