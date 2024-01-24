import os

from dagster import Definitions
from dagster_dbt import DbtCliResource

from swile_dagster.assets import export_to_csv, raw_shops, raw_transactions, swile_dbt_assets
from swile_dagster.constants import dbt_project_dir
from swile_dagster.schedules import schedules

defs = Definitions(
    assets=[raw_transactions, raw_shops, swile_dbt_assets, export_to_csv],
    schedules=schedules,
    resources={
        "dbt": DbtCliResource(project_dir=os.fspath(dbt_project_dir), profile_dir=os.fspath(dbt_project_dir)),
    },
)
