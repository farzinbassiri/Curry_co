
# Carregando os dados e fazendo limpeza inicial

# bibliotecas necessárias
import pandas as pd
import re
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import folium
from haversine import haversine
import streamlit as st
from PIL import Image
from streamlit_folium import folium_static
import numpy as np


st.set_page_config(page_title= 'Visão Restaurantes', layout='wide')
# lendo o arquivo importado

df = pd.read_csv('Dataset\\train.csv')
df1 = df.copy()
#print(df1.dtypes)
#print(df1.head(5))

# função para eliminar linhas que contém conteúdo inválido
    # entradas:
    #   conteudo a ser eliminado -->  texto
    #   coluna a ser limpa --> texto
    #   o dataframe deve ser global.
def limpa_vazios(conteudo_invalido, coluna):
    global df1
    
    linhas_validas = df1[coluna] != conteudo_invalido
    #transfere para o dataframe apenas as linhas que contém dados
    df1 = df1.loc[linhas_validas, :]
    # refaz o index depois de remover as linhas inválidas
    df1 = df1.reset_index(drop = True)
    #print('Linhas com conteúdo inválido (', conteudo_invalido ,') na coluna', coluna, 'foram removidas com sucesso.')

# função para transformar typo de dados nas colunas
    # entradas:
    #   conteudo a ser eliminado -->  texto
    #   coluna a ser limpa --> texto
    #   o dataframe deve ser global.
def transforma_tipo(novo_tipo, coluna):
    # transforma a variável para o novo tipo.
    df1[coluna] = df1[coluna].astype(novo_tipo)
    #print('Coluna ', coluna,'foi configurada como: ', novo_tipo)

# eliminando espaços no final de duas colunas
df1.loc[:, 'ID'] = df1.loc[:, 'ID'].str.strip()
df1.loc[:, 'Delivery_person_ID'] = df1.loc[:, 'Delivery_person_ID'].str.strip()
df1.loc[:, 'Festival'] = df1.loc[:, 'Festival'].str.strip()
df1.loc[:, 'Weatherconditions'] = df1.loc[:, 'Weatherconditions'].str.strip('conditions ')

# primeiro precisa excluir valores faltantes preenchidos com texto:'NaN ' - houve erro ao converter indicando essa necessidade
limpa_vazios('NaN ', 'Delivery_person_Age')
limpa_vazios('NaN ', 'Delivery_person_Ratings')
limpa_vazios('NaN ', 'multiple_deliveries')
limpa_vazios('conditions NaN', 'Weatherconditions')
limpa_vazios('NaN', 'Weatherconditions')
limpa_vazios('NaN ', 'Road_traffic_density')
limpa_vazios('NaN ', 'City')
limpa_vazios('NaN ', 'Festival')
limpa_vazios('NaN', 'Festival')

transforma_tipo(int, 'Delivery_person_Age')
transforma_tipo(int, 'multiple_deliveries')
transforma_tipo(float, 'Delivery_person_Ratings')

# transforma coluna de datas para o formato de data
df1['Order_Date'] = pd.to_datetime( df['Order_Date'], format='%d-%m-%Y' )

# Comando para remover o texto de números
df1.loc[:, 'Time_taken(min)'] = df1.loc[:, 'Time_taken(min)'].str.strip('(min) ')
transforma_tipo(int, 'Time_taken(min)')

df1.loc[:,'Road_traffic_density'] = df1.loc[:, 'Road_traffic_density'].str.strip()
#print('Limpeza dos dados realizada com sucesso!')


#*********************#
#    Barra Lateral    #
#*********************#

st.header('Marketplace - Visão Restaurantes')

image = Image.open('logo.jpg')
st.sidebar.image(image, width=120)

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""___""")
st.sidebar.markdown('## Selecione uma data limite')

# seleção da data de interesse pelo usuário
date_slider = st.sidebar.slider(
    'Até qual valor?',
    min_value = pd.datetime(2022, 2, 1),
    max_value = pd.datetime(2022, 4, 6),
    value = pd.datetime(2022, 3, 1),
    format = 'DD-MM-YYYY')
st.sidebar.markdown("""___""")

# seleção da condição de transito 
traffic_options = st.sidebar.multiselect(
    'Quais as condições do trânsito?',
    ['Low', 'Medium', 'High', 'Jam'],
    default = ['Low', 'Medium', 'High', 'Jam'])
st.sidebar.markdown("""___""")
st.sidebar.markdown('###### Powered by Comunidade DS')

# aplica os filtros do sidebar na tabela de dados
# filtro de data
linhas_selecionadas = df1['Order_Date'] < date_slider 
df1 = df1.loc[linhas_selecionadas,:]
#testa mostrando os dados
#st.dataframe(df1.head())

#filtro de transito
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas,:]
#st.dataframe(df1.head())
#st.header(traffic_options)
#**********************************
#    Layout usando o Streamlit    #
#**********************************

#criando abas

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '-', '-'])

# separa os códigos para cada aba
# todo código que estiber em 'with tab1 vai aparecer naquela aba
with tab1:
    # bloco #1 de informação
    with st.container():
        st.title('Overall Metrics')
        st.markdown("""___""")
        
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        # Quantidade de Entregadores únicos
        with col1:
            delivery_unique = len(df1.loc[:,'Delivery_person_ID'].unique())
            col1.metric('Entregadores Únicos', delivery_unique)
        # monta as colunas de interesse no filtro
        with col2:
            colunas = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']

            # calcula a distancia entre os pontos de partida (restaurante) e chagada (cliente)
            # usando a função 'haversine' que tem como entradas latitude e longitude de saida e de chegada, a saída é a distancia, por padrão é em km
            # axis=1 para indicar que as varáveis estão em forma de coluna
            df1['distance'] = df1.loc[:, colunas].apply(lambda x: 
                                                  haversine(
                                                      (x['Restaurant_latitude'], x['Restaurant_longitude']),
                                                      (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1)

            df_mean = np.round(df1.loc[:,'distance'].mean(), 2)
            col2.metric('Distância Média das Entregas', df_mean)
            
        with col3:
            colunas = ['Festival', 'Time_taken(min)']
            df_mean = df1.loc[:, colunas].groupby(['Festival']).agg({'Time_taken(min)': ['mean', 'std']})
            df_mean.columns  = ['avg_time', 'std_time']
            df_mean = df_mean.reset_index()
            df_mean = np.round(df_mean.loc[df_mean['Festival'] == 'Yes', 'avg_time'], 2)

            col3.metric('Tempo médio de entrega com festival', df_mean)
            
        with col4:
            colunas = ['Festival', 'Time_taken(min)']
            df_mean = df1.loc[:, colunas].groupby(['Festival']).agg({'Time_taken(min)': ['mean', 'std']})
            df_mean.columns  = ['avg_time', 'std_time']
            df_mean = df_mean.reset_index()
            df_mean = np.round(df_mean.loc[df_mean['Festival'] == 'Yes', 'std_time'], 2)

            col4.metric('Desvio padrão do Tempo de entrega com festival', df_mean)
            
        with col5:
            colunas = ['Festival', 'Time_taken(min)']
            df_mean = df1.loc[:, colunas].groupby(['Festival']).agg({'Time_taken(min)': ['mean', 'std']})
            df_mean.columns  = ['avg_time', 'std_time']
            df_mean = df_mean.reset_index()
            df_mean = np.round(df_mean.loc[df_mean['Festival'] == 'No', 'avg_time'], 2)

            col5.metric('Tempo médio de entrega sem festival', df_mean)
        with col6:
            colunas = ['Festival', 'Time_taken(min)']
            df_mean = df1.loc[:, colunas].groupby(['Festival']).agg({'Time_taken(min)': ['mean', 'std']})
            df_mean.columns  = ['avg_time', 'std_time']
            df_mean = df_mean.reset_index()
            df_mean = np.round(df_mean.loc[df_mean['Festival'] == 'No', 'std_time'], 2)

            col6.metric('Desvio padrão do Tempo de entrega sem festival', df_mean)
            
    with st.container():
        st.title('Tempo médio de entrega por cidade')
        colunas = ['City', 'Time_taken(min)']
        df_mean = df1.loc[:, colunas].groupby('City').agg({'Time_taken(min)': ['mean', 'std']})
        df_mean.columns  = ['avg_time', 'std_time']
        df_mean = df_mean.reset_index()
        fig = go.Figure()
        fig.add_trace(go.Bar(name='Tempo Médio', x=df_mean['City'], y=df_mean['avg_time'], error_y=dict(type='data', array=df_mean['std_time'])))
        st.plotly_chart(fig)
        st.markdown("""___""")
            
       
