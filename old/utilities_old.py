def metabase_card(querynumber, company):
    import requests
    import pandas as pd
    import os

    if company == 'pagarme':
        metabase_login = os.getenv('pagarme_metabase_login')
        metabase_pw = os.getenv('pagarme_metabase_pw')
        endpoint = 'data.pagarme.net'
    elif company == 'ton':
        metabase_login = os.getenv('metabase_ton_login')
        metabase_pw = os.getenv('metabase_ton_pwd')
        endpoint = 'ton.com.br'


    ## Conect to metabase API and extract json
    metabase_url = 'https://metabase.' + endpoint + '/api/session'
    auth_resp = requests.post(url=metabase_url, json={"username": metabase_login, "password": metabase_pw},
                              headers={
    	                          "Content-Type": "application/json"
                              })
    respAuth = auth_resp.json()

    metabase_url_query = 'https://metabase.' + endpoint + '/api/card/' + querynumber + '/query/json'

    auth_resp_query = requests.post(url=metabase_url_query, headers={
    	"X-Metabase-Session": respAuth['id']
    })
    respQuery = auth_resp_query.json()

    #_old    
        # if company == 'pagarme':
        #     columns = respQuery['data']['columns']
        #     rows = respQuery['data']['rows']
        #     df = pd.DataFrame(data=rows, columns=columns)
        # elif company == 'ton':
        #     columns = []
        #     for i in range(0, len(respQuery['data']['cols'])):
        #         cols = respQuery['data']['cols'][i]['display_name']
        #         columns.append(cols)

    df = pd.DataFrame(respQuery)

    return df

def metabase_direct(db, query_name, query_dir, company, format_str = None, offset_key = False, grouped = True):
    # HerokuDB = 100
    import requests
    import pandas as pd
    import os
    import math

    query_path = (os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', "queries", query_dir)), query_name))
    query = open(query_path, 'r', encoding='utf-8-sig')
    query = query.read()

    if company == 'pagarme':
        metabase_login = os.getenv('pagarme_metabase_login')
        metabase_pw = os.getenv('pagarme_metabase_pw')
        endpoint = 'data.pagarme.net'
    elif company == 'ton':
        metabase_login = os.getenv('metabase_ton_login')
        metabase_pw = os.getenv('metabase_ton_pwd')
        endpoint = 'ton.com.br'

    ## Conect to metabase API and extract json
    metabase_url = 'https://metabase.' + endpoint + '/api/session'
    auth_resp = requests.post(url=metabase_url, json={"username": metabase_login, "password": metabase_pw},
                              headers={
    	                          "Content-Type": "application/json"
                              })
    respAuth = auth_resp.json()

    df = pd.DataFrame()
    i = 0
    if grouped == True:
        k = 10000
    else:
        k = 2000

    while (len(df) % k == 0 and len(df) != 0) or i == 0:

        if offset_key == True:
            if format_str != None:
                query_i = query.format(format_str, k*i)
            else:
                query_i = query.format(k*i)
        elif format_str != None:
            query_i = query.format(format_str)
        else:
            query_i = query

        params = {
        "database": db,
        "type": "native",
        "native": {
            "query": query_i
        }
        }

        res = requests.post('https://metabase.' + endpoint + '/api/dataset/', 
                    headers = {'Content-Type': 'application/json',
                                'X-Metabase-Session': respAuth['id']
                                },
                    json=params
                    )

        respQuery = res.json()

        if company == 'pagarme':
            columns = respQuery['data']['columns']
        elif company == 'ton':
            columns = []
            for j in range(0,len(respQuery['data']['cols'])):
                columns.append(respQuery['data']['cols'][j]['display_name'])

        rows = respQuery['data']['rows']

        df = df.append(pd.DataFrame(data=rows, columns=columns))
        i += 1

        print(str(i) + ' - df length is ' + str(len(df)) + ' rows')

    
    return df

def query_data(db, query_dir, query_name, t=3, format_str = None):
    import os, psycopg2, json
    import pandas as pd
    from simple_salesforce import Salesforce

    print('Function query_data starting...')

    db = db.lower()

    credentials = {
        'salesforce' : 
            {'login' : 'cicero_sf_login', 'pw' : 'cicero_sf_pw', 'token' : 'cicero_sf_security'},
        'cicero' : 
            {'login' : 'cic_ton_login', 'pw' : 'cic_ton_pw', 'host' : 'cic_ton_host', 'port' : 'cic_ton_port', 'db' : 'cic_ton_db'},
        'datarock' : 
            {'login' : 'datarock_login', 'pw' : 'datarock_pw', 'host' : 'datarock_host', 'port' : 'datarock_port', 'db' : 'datarock_dbname'},
        'biton' : 
            {'login' : 'biton_user', 'pw' : 'biton_pw', 'host' : 'biton_host', 'port' : 'biton_port', 'db' : 'biton_dbname'},
        'stonelog' : 
            {'login' : 'nathan_user_2', 'pw' : 'nathan_password_2', 'host' : 'nathan_host_2', 'port' : 'nathan_port', 'db' : 'nathan_dbname_2'},
        'controlatonia' :
            {'login' : 'ctrl_login', 'pw' : 'ctrl_pw', 'host' : 'ctrl_host', 'port' : 'ctrl_port', 'db' : 'ctrl_db'},
    }

    print('Credentials found\nTrying connection to ' + str(db.upper()) + ' DB...')

    login = os.getenv(credentials[db]['login'])
    pw = os.getenv(credentials[db]['pw'])

    if db == 'salesforce':
        token = os.getenv(credentials[db]['token'])
        conn = Salesforce(username=login, password=pw, security_token=token)
        database_name = 'SALESFORCE'
    
    else:
        host = os.getenv(credentials[db]['host'])
        port = os.getenv(credentials[db]['port'])
        database_name = os.getenv(credentials[db]['db'])
        conn = psycopg2.connect(user=login, password=pw, host=host, port=port, dbname=database_name)
    
    print('Connection to '+str(db.upper())+' DB ('+str(database_name.upper())+') estabilished')

    query_path = (os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', "queries", query_dir)), query_name))
    query = open(query_path, 'r', encoding='utf-8-sig')
    query = query.read()

    print('Query path found')

    if format_str != None:
        query = query.format(format_str)

    max_tries = t
    i=1
    j=0
    while i <= max_tries:
        try:
            print('Querying data...')

            if db == 'salesforce':
                df = pd.DataFrame(conn.query_all(query)['records']).drop(columns='attributes')
            else:
                df = pd.read_sql(query, conn)

            i=max_tries+1
        except:
            print('Query failed! Starting retry number ' + str(i-1) + ' of ' + str(max_tries))
            j+=1
            i+=1


    if j >= max_tries:
        print('Function query_data FAILED!')
    else:
        print('Data from '+query_name+' queried\nFunction query_data finished with 0 errors')

    if db != 'salesforce':
        conn.close()
        print('Connection to '+str(db.upper())+' DB ('+str(database_name.upper())+') closed')

    return df

def paste_to_sheets(df, gsheet, sheet_name, clear = False, h = True, i = False, row = 1, col = 1, row_c = 'A1', col_c = None):
    import os, pygsheets
    
    gs = pygsheets.authorize(service_file = os.getcwd() + r"\controlatonia\docs\sheets_api_creds.json")
    sh = gs.open(gsheet)
    worksheet = sh.worksheet_by_title(sheet_name)
    if clear == True:
        worksheet.clear(start=row_c, end=col_c)
    worksheet.set_dataframe(df, (row, col), copy_head = h, copy_index = i)

    print(
        'Dataframe printed to ' + 
        str(gsheet) +
        ' - ' +
        str(sheet_name)
        )

def get_from_sheets(gsheet, sheet_name):
    import os, pygsheets
    import pandas as pd

    gs = pygsheets.authorize(service_file = os.getcwd() + r"\controlatonia\docs\sheets_api_creds.json")
    sh = gs.open(gsheet)
    worksheet = sh.worksheet_by_title(sheet_name)
    df = pd.DataFrame(worksheet.get_all_records())

    return df

def pause(df_name):
    programPause = input(
        "Press the <ENTER> key to continue when " + df_name + " has been filled."
    )