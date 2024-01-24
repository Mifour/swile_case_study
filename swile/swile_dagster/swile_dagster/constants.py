import os
from pathlib import Path

from dagster_dbt import DbtCliResource

dbt_project_dir = Path(__file__).joinpath("..", "swile_dbt").resolve()
dbt = DbtCliResource(project_dir=os.fspath(dbt_project_dir), profile_dir=os.fspath(dbt_project_dir))

# If DAGSTER_DBT_PARSE_PROJECT_ON_LOAD is set, a manifest will be created at run time.
# Otherwise, we expect a manifest to be present in the project's target directory.
if os.getenv("DAGSTER_DBT_PARSE_PROJECT_ON_LOAD"):
    try:
        dbt_manifest_path = (
            dbt.cli(
                ["parse", "--project-dir", os.fspath(dbt_project_dir), "--profiles-dir", os.fspath(dbt_project_dir), "--no-quiet",],
                target_path=Path("target"),
            )
            .wait()
            .target_path.joinpath("manifest.json")
        )
    except Exception as e:
        print(e)
        with open("/opt/dagster/app/swile_dagster/swile_dagster/swile_dbt/target/dbt.log", "r") as log:
            print(log.read())
        raise e
else:
    dbt_manifest_path = dbt_project_dir.joinpath("target", "manifest.json")


# Minio connection

MINIO_CONF = {
    "endpoint": f"{os.getenv('MINIO_HOST')}:9000",
    "secure": False,
    "access_key": os.getenv("MINIO_ROOT_USER"),
    "secret_key": os.getenv("MINIO_ROOT_PASSWORD"),
}
MINIO_BUCKET_NAME = "bucket"
MINIO_TRANSACTION_FOLDER_PATH = "transactions/"

# Postgres connection
DAGSTER_POSTGRES_HOSTNAME = os.getenv("POSTGRES_HOSTNAME")
DAGSTER_POSTGRES_USER = os.getenv( "DAGSTER_POSTGRES_USER")
DAGSTER_POSTGRES_PASSWORD = os.getenv( "DAGSTER_POSTGRES_PASSWORD")
DAGSTER_POSTGRES_DB = os.getenv( "DAGSTER_POSTGRES_DB")
POSTGRES_CONNECTION = f"postgresql://{DAGSTER_POSTGRES_USER}:{DAGSTER_POSTGRES_PASSWORD}@{DAGSTER_POSTGRES_HOSTNAME}:5432/{DAGSTER_POSTGRES_DB}"

# INSEE connection
INSEE_CONSUMER_KEY = os.getenv("INSEE_CONSUMER_KEY")
INSEE_CONSUMER_SECRET = os.getenv("INSEE_CONSUMER_SECRET")
