FROM python:3.11-bookworm

# Checkout and install dagster libraries needed to run the gRPC server
# exposing your repository to dagster-webserver and dagster-daemon, and to load the DagsterInstance

RUN pip install \
    setuptools \
    dagster \
    dagster-cloud \
    dagster-dbt \
    dagster-postgres \
    dbt-core\
    dagster-docker \
    dbt-postgres \
    sqlalchemy \
    requests \
    minio

# Add repository code

WORKDIR /opt/dagster/app

COPY . /opt/dagster/app

WORKDIR /opt/dagster/app/swile_dagster

# Run dagster gRPC server on port 4000

EXPOSE 4000

CMD ["dagster", "api", "grpc", "-h", "0.0.0.0", "-p", "4000", "-f", "swile_dagster/definitions.py"]
