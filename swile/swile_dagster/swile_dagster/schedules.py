from dagster_dbt import build_schedule_from_dbt_selection

from swile_dagster.assets import swile_dbt_assets

schedules = [
     build_schedule_from_dbt_selection(
          [swile_dbt_assets],
          job_name="materialize_dbt_models",
          cron_schedule="0 0 * * *",
          dbt_select="fqn:*",
     ),
]
