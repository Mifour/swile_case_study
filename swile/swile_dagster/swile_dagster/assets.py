import io
import json
from time import sleep

import sqlalchemy as sqla
from dagster import AssetExecutionContext, asset
from dagster_dbt import DbtCliResource, dbt_assets, get_asset_key_for_model
from minio import Minio
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import sessionmaker

from swile_dagster.constants import MINIO_CONF, POSTGRES_CONNECTION, dbt_manifest_path, dbt_project_dir
from swile_dagster.helpers import (
    check_bucket_exists,
    create_table_if_not_exists,
    get_insee_headers,
    get_naf_code,
    list_s3_files,
)
from swile_dagster.sa_models import Shop, Transaction


@dbt_assets(manifest=dbt_manifest_path)
def swile_dbt_assets(context: AssetExecutionContext, dbt: DbtCliResource):
    context.log.info(f"reading manifest at {dbt_manifest_path}")
    yield from dbt.cli(["build"], context=context, target_path=dbt_project_dir).stream()


@asset(compute_kind="python")
def raw_transactions(context: AssetExecutionContext) -> None:
    engine = sqla.create_engine(POSTGRES_CONNECTION)
    create_table_if_not_exists(engine, context)
    Session = sessionmaker(engine)
    minio_client = Minio(**MINIO_CONF)
    n = 0

    with Session.begin() as session:
        try:
            for file_name in list_s3_files(minio_client):
                response = minio_client.get_object("bucket", file_name)
                rows = []
                for t in json.loads(response.data.decode()):
                    if Transaction(**t).validate_values():
                        rows.append(t)
                        n += 1
                if rows:
                    session.execute(
                        insert(Transaction).on_conflict_do_nothing(),
                        rows,
                    )
        except Exception as e:
            context.log.error(f"Exception {e}")
        finally:
            if "response" in vars():
                response.close()
                response.release_conn()
            context.log.info(f"ingested {n} transactions from S3")


@asset(compute_kind="python", deps=[raw_transactions,])
def raw_shops(context: AssetExecutionContext) -> None:
    engine = sqla.create_engine(POSTGRES_CONNECTION)
    create_table_if_not_exists(engine, context)
    Session = sessionmaker(engine)
    headers = get_insee_headers(context)

    with Session.begin() as session:
        # fetch only the NAF codes we need
        for chunk in session.execute(
            sqla.select(Transaction.siret.distinct()).where(
                Transaction.siret.not_in(sqla.select(Shop.siret.distinct()))
            )
        ).partitions(100):
            for row in chunk:
                siret = int(row[0])
                if naf_code := get_naf_code(siret, context, headers):
                    session.execute(
                        insert(Shop).on_conflict_do_nothing(),
                        [{"siret": siret, "naf_code": naf_code}],
                    )
                else:
                    context.log.error(f"couldn't get naf code for siret: {siret}")
                sleep(2)  # this should be replaced by a proper rate limiter


@asset(
    compute_kind="python",
    deps=get_asset_key_for_model([swile_dbt_assets], "daily_spent_per_naf_code"),
)
def export_to_csv(context: AssetExecutionContext):
    engine = sqla.create_engine(POSTGRES_CONNECTION)
    minio_client = Minio(**MINIO_CONF)

    check_bucket_exists(minio_client)
    rows = [b"date,naf_code,spent"]
    n = 0
    with engine.connect() as connection:
        for row in connection.execute(
            sqla.text(
                """select _date as "date", naf_code, spent from public.daily_spent_per_naf_code order by 1, 2;"""
            )
        ):
            rows.append(b",".join([str(value).encode() for value in row]))
            n += 1

    content = b"\n".join(rows)
    minio_client.put_object(
        "bucket",
        "export.csv",
        io.BytesIO(content),
        len(content),
        content_type="application/csv",
    )
    context.log.info(f"exported {n} rows onto S3 at bucket/export.csv")
