import base64

import requests
import sqlalchemy as sqla
from dagster import AssetExecutionContext
from minio import Minio
from sqlalchemy.engine import Engine
from sqlalchemy.sql import exists, select

from swile_dagster.constants import INSEE_CONSUMER_KEY, INSEE_CONSUMER_SECRET
from swile_dagster.sa_models import Shop, Transaction


def create_table_if_not_exists(engine: Engine, context: AssetExecutionContext):
    insp = sqla.inspect(engine)
    with engine.connect() as connection:
        # check if schema exists too
        if not insp.has_schema("public"):
            session.execute(sqla.text("CREATE SCHEMA public AUTHORIZATION CURRENT_USER;"))
            connection.commit()
        if not insp.has_table("transaction", schema="public"):
            # clean start
            connection.execute(sqla.text("DROP type if exists typeenum;"))
            connection.execute(sqla.text("DROP type if exists statusenum;"))
            connection.commit()
            Transaction.__table__.create(bind=engine)
            connection.commit()
            context.log.info("CREATED TABLE transaction")
        if not insp.has_table("shop", schema="public"):
            Shop.__table__.create(bind=engine)
            connection.commit()
            context.log.info("CREATED TABLE shop")
        


def check_bucket_exists(client: Minio):
    if not client.bucket_exists("transactions"):
        raise ValueError("Bucket 'transactions' does not exist.")


def list_s3_files(client: Minio) -> list[str]:
    check_bucket_exists(client)
    return [obj.object_name for obj in client.list_objects("transactions", "transactions/")]


def get_insee_headers(context: AssetExecutionContext) -> dict[str, str]:
    context.log.info(f"encoding {INSEE_CONSUMER_KEY}:{INSEE_CONSUMER_SECRET}")
    encoded = base64.b64encode(f"{INSEE_CONSUMER_KEY}:{INSEE_CONSUMER_SECRET}".encode())
    response = requests.post(
        "https://api.insee.fr/token",
        headers={"Authorization": b"Basic " + encoded},
        data="grant_type=client_credentials",
    )
    if not response.ok:
        raise ValueError(f"invalid authentication from INSEE: {response.content}")
    bearer = response.json()["access_token"]
    return {"Accept": "application/json", "Authorization": f"Bearer {bearer}"}


def get_naf_code(siret: int, context: AssetExecutionContext, headers: dict) -> str | None:
    response = requests.get(
        f"https://api.insee.fr/entreprises/sirene/V3/siret/{siret}/",
        headers=headers,
    )
    if not response.ok:
        context.log.error(response.content)
        return None
    return response.json()["etablissement"]["uniteLegale"][
        "activitePrincipaleUniteLegale"
    ]
