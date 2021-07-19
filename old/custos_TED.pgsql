with companies as (
  select
    id,
    cnpj
  from pagarme_replication.mongo_companies
  where
    status = 'active' and
    type = 'mei'
),
activeclients as (
    select
    	company_id
    from companies
    	left join pagarme_replication.live_transactions as transactions
    	 on companies.id = transactions.company_id
    where 
    	status in ('paid', 'refunded', 'chargedback')
    group by 1
),

aux_teds as (
    select
    	 count(distinct t.company_id) as clientes_com_ted
    	,count(t.id) as num_teds
    	,sum(cost)/100. as custo_teds
    from activeclients ac
    	left join pagarme_replication.live_transfers as t
    		on ac.company_id = t.company_id
    where 
    	type <> 'inter_recipient'
    	and status <> 'canceled'
    	and bank_response_code is not null
    	and (created_at at time zone 'utc' at time zone 'america/sao_paulo')::date between '{}' and '{}'
),

aux_custo_medio as (
    select 
        custo_teds/num_teds as custo_medio_teds
        ,clientes_com_ted*2 as num_teds_resp_pagarme
        ,num_teds
    from aux_teds
)

select
    (num_teds - num_teds_resp_pagarme) * custo_medio_teds
from aux_custo_medio