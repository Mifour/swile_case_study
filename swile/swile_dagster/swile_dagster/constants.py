import os
from pathlib import Path

from dagster_dbt import DbtCliResource

dbt_project_dir = Path(__file__).joinpath("..", "..", "..").resolve()
dbt = DbtCliResource(project_dir=os.fspath(dbt_project_dir))

# If DAGSTER_DBT_PARSE_PROJECT_ON_LOAD is set, a manifest will be created at run time.
# Otherwise, we expect a manifest to be present in the project's target directory.
if os.getenv("DAGSTER_DBT_PARSE_PROJECT_ON_LOAD"):
    dbt_manifest_path = (
        dbt.cli(
            ["--quiet", "parse"],
            target_path=Path("target"),
        )
        .wait()
        .target_path.joinpath("manifest.json")
    )
else:
    dbt_manifest_path = dbt_project_dir.joinpath("target", "manifest.json")


# Minio connection
MINIO_CONF = {
    "endpoint": "localhost:9000",
    "secure": False,
    "access_key": "minio",
    "secret_key": "password",
}

# Postgres connection
POSTGRES_CONNECTION = "postgresql://swile_writer_user:password@127.0.0.1:5432/swile"

# INSEE connection
INSEE_CONSUMER_KEY = "RRLpHph_qqLVFvW5kdSHfD0pV3Ua"
INSEE_CONSUMER_SECRET = "GCyMzihpqXe3FEzmOxrY81rfHA4a"
