{{ config(materialized='materialized_view', schema='public', on_configuration_change = 'apply') }}
-- somehow, the materialized view will stiil be inside the 'default_public' schema

with requires_raw_transactions as (

    select {{ "'" ~ source('swile', 'raw_transactions').name ~ "'" }}
    -- pointless sql statement but needed to make dagster set operation
    -- raw_transactions & raw_shops as upstreams for this job

),

requires_raw_shops as (

    select  {{ "'" ~ source('swile', 'raw_shops').name ~ "'" }}

),

all_dates as(
    select i::date as "date" from generate_series(
        '2023-10-01', -- those should be parametrised or automatically determined from transaction
        '2023-12-31',
        '1 day'::interval
    ) i
), 

filtered_transaction as (

    select
        amount,
        status,
        created_at,
        siret
    from {{ source('swile', 'transaction') }}
    where status::text ilike 'CAPTURED'
    -- Is returned or declined money considered to be spent money? Ask the Product Owner or the Client.

),

all_shops as (

    select
        siret,
        naf_code
    from {{ source('swile', 'shop') }}

),

jointure as (

    select
        filtered_transaction.created_at::date as "_date",
        filtered_transaction.siret as "transaction_siret",
        all_shops.siret as "shop_siret",
        all_shops.naf_code as "naf_code",
        filtered_transaction.amount
    from filtered_transaction
    full join all_dates on all_dates.date = filtered_transaction.created_at::date
    cross join all_shops

)

select 
    _date, 
    naf_code, 
    round(sum(case when shop_siret = transaction_siret then amount else 0 end)::numeric, 2) as spent
from jointure 
group by _date, naf_code
