def os_capitalization():

    import pandas as pd, numpy as np, os, time, datetime, math, xlwt, glob, psycopg2, pygsheets
    from pandas.tseries.offsets import MonthEnd
    import utilities as utl
    print (__file__)

    today = pd.datetime.today()

    tabela_custos_log = utl.get_from_sheets('Report Logistics', 'custos_log_operador_uf')
    tabela_custos_log = tabela_custos_log.set_index('UF_R')

    # custos_os_log = utl.metabase_card('107', 'ton') query foi atualizada com informações de preços Stone Log para query 677
    custos_os_log = utl.metabase_card('677', 'ton')
    custos_os_log = custos_os_log.set_index('coluna_tabela_log')
    custos_os_log['custo_transporte'] = pd.DataFrame(np.zeros((len(custos_os_log.index), 1)))

    # novos_clientes = utl.metabase_card('349', 'ton')
    novos_clientes_cnpj = utl.metabase_card('364', 'ton')

    df = utl.get_from_sheets('Report Logistics', 'custos_log_daily')
    max_date = df['data_cobranca'].max()
    df = df[df['data_cobranca'] < max_date]

    df2 = utl.get_from_sheets('Report Logistics', 'custos_log_daily - new_customers')
    max_date2 = df2['data_cobranca'].max()
    df2 = df2[df2['data_cobranca'] < max_date2]

    custos_os_log = custos_os_log[custos_os_log['data_cobranca'] >= max_date]

    i = 1
    print('start custos_os_log iteration')
    for index, row in custos_os_log.iterrows():
        try:
            custos_os_log['custo_transporte'] = np.where(custos_os_log['regiao'] == row['regiao'], np.where(custos_os_log.index == index, tabela_custos_log.loc[row['regiao'], index], custos_os_log['custo_transporte']),custos_os_log['custo_transporte'])
        except KeyError:
            custos_os_log['custo_transporte'] = np.where(custos_os_log['regiao'] == row['regiao'], np.where(custos_os_log.index == index, 0, custos_os_log['custo_transporte']),custos_os_log['custo_transporte'])
        i += 1
        print('custos_os_log iteration ' + str(i))

    custos_os_log['data_cobranca'] = pd.to_datetime(custos_os_log['data_cobranca'], errors = 'coerce').dt.date
    custos_os_log['custo_transporte'] = pd.to_numeric(custos_os_log['custo_transporte'])
    
    custos_os_log_daily = custos_os_log[['op_log', 'data_cobranca', 'custo_transporte']].reset_index()
    custos_os_log_daily['op_log'] = np.where(custos_os_log_daily['coluna_tabela_log'] == 'CORREIO (FLASH)', 'CORREIO (FLASH)', np.where(custos_os_log_daily['coluna_tabela_log'] == 'CORREIO (PAYTEC)', 'CORREIO (PAYTEC)', custos_os_log_daily['op_log']))
    
    novos_clientes = custos_os_log[custos_os_log['numeroos'].isin(novos_clientes_cnpj['numeroos'])]
    novos_clientes = novos_clientes[['op_log', 'data_cobranca', 'custo_transporte']].reset_index()
    novos_clientes['op_log'] = np.where(novos_clientes['coluna_tabela_log'] == 'CORREIO (FLASH)', 'CORREIO (FLASH)', np.where(novos_clientes['coluna_tabela_log'] == 'CORREIO (PAYTEC)', 'CORREIO (PAYTEC)', novos_clientes['op_log']))
    
    custos_os_log_daily = custos_os_log_daily.groupby(['op_log', 'data_cobranca']).sum().reset_index()
    custos_os_log_daily = df.append(custos_os_log_daily)

    novos_clientes = novos_clientes[novos_clientes['data_cobranca'] >= pd.to_datetime(max_date2).date()]
    novos_clientes_daily = novos_clientes.groupby(['op_log', 'data_cobranca']).sum().reset_index()
    novos_clientes_daily = df2.append(novos_clientes_daily)

    print('Tabela "modelo diário - novos clientes" (novos_clientes_daily) tem ' + str(novos_clientes_daily['data_cobranca'].count()) + ' linhas.')
    print('Tabela "modelo diário - total" (custos_os_log_daily) tem ' + str(custos_os_log_daily['data_cobranca'].count()) + ' linhas.')

    utl.paste_to_sheets(custos_os_log_daily, 'Report Logistics', 'custos_log_daily')

    utl.paste_to_sheets(novos_clientes_daily, 'Report Logistics', 'custos_log_daily - new_customers')

    print('Data de geração do relatório: ' + str(today))


os_capitalization()

