from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd
import requests
import numpy as np


def getCategories(siteName):
    ids = []

    if siteName == 'delfina':
        base_url = 'https://www.vendus.pt/ws/v1.1/products/categories/?api_key=56d31f404db2dfb6e10609ba2081dcfd'
        params = dict()
        r = requests.get(base_url, params=params)
        j = r.json()
        ids = pd.DataFrame.from_dict(j)

        ids.index.name = None
        ids = ids[['title', 'id']]
        ids.columns = ['Categoria', 'CategoriaID']

    return ids


def getProdutos(siteName):
    ids = getCategories(siteName)

    if siteName == 'delfina':
        base_url = "https://www.vendus.pt/ws/v1.1/products/?api_key=56d31f404db2dfb6e10609ba2081dcfd"
        params = dict()
        params["per_page"] = 1000

        df_delfina = pd.DataFrame()

        for i in range(len(ids)):
            params["category_id"] = ids['CategoriaID'].iloc[i]
            r = requests.get(base_url, params=params)
            j = r.json()
            df = pd.DataFrame.from_dict(j)
            df['cat'] = ids['Categoria'].iloc[i]
            df_delfina = pd.concat([df_delfina, df])

        df_delfina = df_delfina[['reference', 'title', 'gross_price', 'cat']]
        df_delfina.columns = ['Referencia', 'Nome', 'Preco', 'Categoria']
        df_delfina.reset_index(inplace=True)
        df_delfina = df_delfina[['Referencia', 'Nome', 'Preco', 'Categoria']]

    return df_delfina


def getProdutosM(siteName):
    if siteName == 'minipreco':
        urls = [
            'https://www.minipreco.pt/produtos/frutas-e-vegetais/frutas/c/WEB.001.001.00000',
            'https://www.minipreco.pt/produtos/frutas-e-vegetais/vegetais/c/WEB.001.002.00000',
            'https://www.minipreco.pt/produtos/mercearia/oleo-azeite-e-vinagre/c/WEB.003.002.00000',
            'https://www.minipreco.pt/produtos/padaria-e-pastelaria/c/WEB.002.000.00000',
            'https://www.minipreco.pt/produtos/talho-e-peixaria/c/WEB.022.000.00000',
            'https://www.minipreco.pt/produtos/laticinios-e-ovos/c/WEB.005.000.00000',
            'https://www.minipreco.pt/produtos/mercearia/c/WEB.003.000.00000',
            'https://www.minipreco.pt/produtos/charcutaria-e-queijos/c/WEB.021.000.00000',
            'https://www.minipreco.pt/produtos/bebidas-e-garrafeira/c/WEB.007.000.00000',
            'https://www.minipreco.pt/produtos/gelados-e-congelados/c/WEB.006.000.00000',
            'https://www.minipreco.pt/produtos/pronto-a-comer/c/WEB.012.000.00000',
            'https://www.minipreco.pt/produtos/bebe-e-crianca/c/WEB.008.000.00000',
            'https://www.minipreco.pt/produtos/limpeza-e-cuidado-do-lar/c/WEB.011.000.00000',
            'https://www.minipreco.pt/produtos/higiene-e-beleza/c/WEB.009.000.00000',
            'https://www.minipreco.pt/produtos/equilibrio-e-bio/c/WEB.019.000.00000',
            'https://www.minipreco.pt/produtos/saude/c/WEB.018.000.00000',
            'https://www.minipreco.pt/produtos/bebidas-e-garrafeira/refrigerantes/c/WEB.007.003.00000',
            'https://www.minipreco.pt/produtos/laticinios-e-ovos/leite/c/WEB.005.001.00000'
        ]

        categorias = [
            'frutas', 'vegetais', 'azeite', 'padaria', 'talho_e_peixaria', 'laticinios',
            'mercearia', 'charcutaria', 'bebidas', 'gelados', 'pronto_a_comer', 'bebe',
            'limpeza', 'higiene', 'equilibrio', 'saude', 'refrigerantes', 'leite'
        ]

        mptb = pd.DataFrame()

        for i in range(len(urls)):
            req = urlopen(urls[i]).read()
            soup = BeautifulSoup(req, "lxml")

            prices = []
            for links in soup.findAll('p', 'pricePerKilogram'):
                prices.append(str(links)[29:-6])

            details = []
            for links in soup.findAll('span', 'details'):
                details.append(str(links)[27:-7])

            d = {'Produto': details[:-1], 'Price': prices}
            aux_df = pd.DataFrame(data=d, index=None)

            aux_df['Categoria'] = categorias[i]
            aux_df['Unidade'] = ''
            aux_df['New Price'] = ''

            for j in range(len(aux_df)):
                aux = str(aux_df['Price'][j])
                aux_price = str(aux_df['Price'][j])[0:aux.find(' ')]
                aux_unidade = str(aux_df['Price'][j])[aux.find(' ') + 1:]

                aux_df['New Price'][j] = aux_price
                aux_df['New Price'][j] = aux_df['New Price'][j].replace(',', '.')

                try:
                    aux_df['New Price'][j] = float(aux_df['New Price'][j])
                except:
                    print('Erro em: ' + str(aux_df['Produto'][j]) + ' ' + str(aux_df['Price'][j]))

                aux_df['Unidade'][j] = aux_unidade

            mptb = pd.concat([mptb, aux_df])

        mptb.reset_index(inplace=True)
        mptb = mptb[['Produto', 'Price', 'Unidade', 'New Price', 'Categoria']]

    return mptb


def getProdutosF(siteName):
    df_delfina = getProdutos(siteName)
    mptb = getProdutosM(siteName)

    if siteName == 'filtrar':
        extras = ['\t\t', 'HORTA DO DIA ', ' Importada', ' Preta']

        for i in range(len(mptb)):
            for j in range(len(extras)):
                mptb.loc[i, 'Produto'] = mptb.loc[i, 'Produto'].replace(extras[j], '')
                mptb.loc[i, 'Produto'] = mptb.loc[i, 'Produto'].lower()
                aux = mptb.loc[i, 'Produto']
                if mptb.loc[i, 'Produto'].find('(') != -1:
                    aux = aux[0:mptb.loc[i, 'Produto'].find('(') - 1]
                    mptb.loc[i, 'Produto'] = aux

        for i in range(len(df_delfina)):
            for j in range(len(extras)):
                df_delfina.loc[i, 'Nome'] = df_delfina.loc[i, 'Nome'].replace(extras[j], '')
                df_delfina.loc[i, 'Nome'] = df_delfina.loc[i, 'Nome'].lower()

    return mptb
