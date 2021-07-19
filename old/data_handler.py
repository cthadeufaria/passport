import pandas as pd, utilities as utl, numpy as np
import glob, os, datetime, pyxlsb
from pandas.tseries.offsets import MonthBegin, MonthEnd


# parameters:
last_month = datetime.datetime.today().date() - MonthEnd(1)
year = last_month.year
month = last_month.month
month_dict = {
    "JAN" : 1, "FEV" : 2, "MAR" : 3, "ABR" : 4, 
    "MAI" : 5, "JUN" : 6, "JUL" : 7, "AGO" : 8, 
    "SET" : 9, "OUT" : 10, "NOV" : 11, "DEZ" : 12,
}
pdca = 127
ignore_supplier = [
    'CRÉD PIS/COFINS LOG', 'CRÉD PIS/COFINS MKT', 'CRÉD PIS/COFINS RA', 'CRÉD PIS/COFINS TEC', 
'CRÉD PIS/COFINS GA', 'CRÉD PIS/COFINS TELC', 'DESPESAS FINANCEIRAS', 'PESSOAS', 'CRÉD PIS/COFINS DA', 'CAPITALIZAÇÃO RENDA EXTRA', 
'CAPITALIZAÇÃO LOGISTICA', 'JUROS S/APLICACAO FINANCEIRA', 'RECEITA - OUTRAS RECEITAS', 'IMPOSTOS RECEITA', 'RECEITA - ADESÃO'
]


# functions
def etl_1(): # import dictionary

    pass

def etl_2(): # import items table
    # items table query
    items = utl.query_data('controlatonia', 'main', 'items.pgsql')
    
    return items

def etl_3(): # import ledger

    # import last modified ledger data as df
    file_path = glob.glob(os.path.join(
        "G:\\", "Drives compartilhados", "Controlatonia", "6. Demonstrativos", 
        "1. Balanço", str(year)+"."+str(month), "razão", 
        "*.xlsb"
    ))
    file_path.sort(key=os.path.getmtime)
    file_path = file_path[-1]
    print(file_path)
    excel = pd.read_excel(file_path, sheet_name="Relatorio", engine='pyxlsb', skiprows=1)
    print(excel.head())

    # treat ledger data
    adj = pd.DataFrame(None, columns=['Data Contabil', 'Data Postada']) # must have columns in same order as dates_list
    dates_list = [excel[adj.columns[0]], excel[adj.columns[1]]] # list of lists
    i = 0
    # convert dates in string format to datetime
    for l in dates_list:
        adj[adj.columns[i]] = pd.to_datetime(['20'+str(i[7:])+'-'+str(month_dict[i[3:6]])+'-'+str(i[:2]) for i in l])
        i += 1

    for j in range(0, pd.Series(adj.columns).count()):
        excel[adj.columns[j]] = adj[adj.columns[j]]

    excel = excel.loc[excel['Empresa']==pdca]

    # insert classification columns
    dictionary = utl.query_data('controlatonia', 'main', 'dictionary.pgsql')
    excel['Key'] = excel['Conta II']+excel['C.Custo II']
    excel['Gerencial'] = np.where((excel['Conta II'].str[0:1]=='3') | (excel['Conta II'].str[0:1]=='4'), 1, 0)
    df = excel.merge(dictionary[['key', 'class_conta', 'agrupamento', 'pnl', 'payroll']], how='left', left_on='Key', right_on='key') # changing main variable to 'df' so 'excel' is not overwritten
    
    # dictionary missing keys
    missing_keys = df.loc[(df['Gerencial']==1) & (df['key'].isna())].drop_duplicates()
    missing_keys.to_csv(r'G:\Drives compartilhados\Controlatonia\4. DB\export\missing_keys.csv')
    # dictionary's new keys insertion is made through the csv file previously saved (missing_keys.csv)
    # it must be updated manually before appending to existing dictionary

    utl.pause('missing_keys.csv') # pause until missing_keys are filled

    # append missing keys on dictionary
    file_path = glob.glob(os.path.join(
        "G:\\", "Drives compartilhados", "Controlatonia", "4. DB", 
        "import", "missing_keys.csv"
    ))
    file_path = file_path[0]
    new_keys = pd.read_csv(file_path)[['Conta II', 'C.Custo II', 'key', 'class_conta', 'agrupamento', 'pnl', 'payroll']]
    new_keys.columns = dictionary.columns
    dictionary = dictionary.append(new_keys)
    df = excel.merge(dictionary[['key', 'class_conta', 'agrupamento', 'pnl', 'payroll']], how='left', left_on='Key', right_on='key')

    # dictionary missing suppliers
    missing_suppliers = df.loc[(df['Gerencial']==1) & (df['Fornecedor'].isna()) & (~df['agrupamento'].isin(ignore_supplier))].drop_duplicates()
    missing_suppliers.to_csv(r'G:\Drives compartilhados\Controlatonia\4. DB\export\missing_suppliers.csv')
    # new suppliers insertion is made through the csv file previously saved (missing_suppliers.csv)
    # it must be updated manually before appending to existing dictionary

    utl.pause('missing_suppliers.csv') # pause until missing_suppliers are filled

    # append missing keys on dictionary
    file_path = glob.glob(os.path.join(
        "G:\\", "Drives compartilhados", "Controlatonia", "4. DB", 
        "import", "missing_suppliers.csv"
    ))
    file_path = file_path[0]
    new_suppliers = pd.read_csv(file_path)
    new_suppliers.drop(columns=['Unnamed: 0'], inplace=True)
    new_suppliers.columns = df.columns
    for n in new_suppliers['Id da Linha']:
        df['Fornecedor'] = np.where(df['Id da Linha'] == n, new_suppliers['Fornecedor'][new_suppliers['Id da Linha'] == n], df['Fornecedor'])

    
etl_3()


# filter PDCA ledger only (x)
# get latest excel file in directory (x)
# get dictionary as df (x)
# input key columns - including dict. cross (x)
    # key (x)
    # gerencial (x)
    # classe_conta (x)
    # agrupamento (x)
    # pnl (x)
    # payroll (x)
# insert new keys on dictionary (x)
# insert missing suppliers on ledger (x)
# insert ledger on database ()
# treat data when ledger is updated with following version ()