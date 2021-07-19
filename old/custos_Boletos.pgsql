with companies as (
  select id
  from pagarme_replication.mongo_companies
  where
    status in ('active', 'inactive') and
    type = 'mei'
),

aux_num_boletos as (
    select
    	count(CASE WHEN status = 'paid' 
    	    AND payment_method = 'boleto'
    	    AND (created_at at time zone 'utc' at time zone 'america/sao_paulo')::date between '{}' AND '{}' 
    	        THEN t.id end) as num_boletos_pagos
    	,count(CASE WHEN status not in ('paid', 'refused')
    	    AND payment_method = 'boleto'
    	    AND created_at :: timestamp at time zone 'utc' at time zone 'america/sao_paulo' <= (current_timestamp - interval '120 day')
    	        THEN t.id end) as num_boletos_nao_pagos
    	from companies
    		left join pagarme_replication.live_transactions as t
    			on companies.id = t.company_id
)

select
    num_boletos_pagos * 1.45 * (1-0.1425) as custo_boletos_pagos
    ,num_boletos_nao_pagos * 0.14 * (1-0.1425) as custo_boletos_nao_pagos
from aux_num_boletos