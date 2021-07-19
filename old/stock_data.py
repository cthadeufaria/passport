from yahoo_fin import stock_info as si, options
import pandas as pd
import requests
from pybovespa.bovespa import *
from pybovespa.stock import *

# b3(): erro
    #     Traceback (most recent call last):
    #   File "<string>", line 2, in <module>
    #   File "C:\Users\crlst\AppData\Local\Programs\Python\Python38\lib\site-packages\pybovespa\bovespa.py", line 30, in query
    #     xml = self.get_xml(*codes)
    #   File "C:\Users\crlst\AppData\Local\Programs\Python\Python38\lib\site-packages\pybovespa\bovespa.py", line 75, in get_xml
    #     raise BovespaError(e)
    # pybovespa.exceptions.BovespaError: MaxRetryError("HTTPConnectionPool(host='www.bmfbovespa.com.br', port=80): Max retries exceeded with url: /Pregao-Online/ExecutaAcaoAjax.asp?CodigoPapel=PETR3 (Caused by ProtocolError('Connection aborted.', ConnectionResetError(10054, 'Foi forçado o cancelamento de uma conexão existente pelo host remoto', None, 10054, None)))")
def b3(stocks = [None]):

    for s in stocks:
        bovespa = Bovespa()
        stock = bovespa.query(s)
        print(stock.cod, stock.name, stock.last)


def stock_data():

    # df = si.get_quote_table("aapl", dict_result = False)
    df = si.get_data('PETR4.SA', interval = '1d')
    # df = si.get_day_losers()
    print("df")
    print(df)

stock_data()

def options_data():

    print(options.get_options_chain("pbr"))

def historical_data():

    df = pd.read_fwf("COTAHIST_A2020.TXT")
    print(df.head())


########################################
# -*- coding: utf-8 -*-
# Elton Luís Minetto
# import urllib
# from xml.dom import minidom
# from time import sleep
# from os import system

# #adicionar as acoes aqui
# #formato ACAO: [num_acoes,valor_compra,data_compra]
# acoes = {
#     'BBDC4':[100,34.84,'25/04/2008'],
#     'PETR4':[100,42.00,'20/04/2008'],
# }

# def atualiza(acoes):
#     system('clear')
#     url = 'http://www.bovespa.com.br/Mercado/RendaVariavel/InfoPregao/ExecutaAcaoAjax.asp?CodigoPapel='
#     for i in acoes:
#         url += '|'+i
#     f = urllib.urlopen(url)
#     xml = f.read()
#     xmldoc = minidom.parseString(xml)
#     papeis = xmldoc.getElementsByTagName('Papel')
#     #cabecalho
#     print(r'Ação\tValor de Compra\tData da Compra\tQtd\tAtual\tDiferença R$\tDiferença %\tData de Atualização')

#     total_compra = 0.0
#     total_dif_reais = 0.0
#     for i in papeis:
#         codigo = i.attributes['Codigo'].value
#         valor_compra = acoes[codigo][1]
#         qtd_acoes = acoes[codigo][0]
#         data_compra = acoes[codigo][2]
#         valor_atual = i.attributes['Ultimo'].value.replace(',','.')
#         data_atual = i.attributes['Data'].value

#         diferenca_reais = (float(valor_atual) * qtd_acoes) - (valor_compra * qtd_acoes)
#         diferenca_perc = (diferenca_reais*100)/(valor_compra * qtd_acoes)
#         total_compra += valor_compra * qtd_acoes
#         total_dif_reais += diferenca_reais

#         print('%s\t%02f\t%s\t%d\t%s\t%02f\t%02f\t%s' % (codigo,valor_compra,data_compra,qtd_acoes,valor_atual,diferenca_reais,diferenca_perc,data_atual)
# )
#     print('Total de Compra:%02f' % total_compra)
#     print('Total da Diferença em Reais:%02f' % total_dif_reais)
#     total_dif_perc = (total_dif_reais * 100)/total_compra
#     print('Total da Diferença em Percentual:%02f' % total_dif_perc)
#     sleep(1200)

# while 1:
#     atualiza(acoes)