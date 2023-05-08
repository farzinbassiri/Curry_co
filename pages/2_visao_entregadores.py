
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
st.set_page_config(page_title= 'Visão Entregadores', layout='wide')
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

st.header('Marketplace - Visão Entregadores')

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

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

# separa os códigos para cada aba
# todo código que estiber em 'with tab1 vai aparecer naquela aba
with tab1:
    # bloco #1 de informação
    with st.container():
        st.title('Overall Metrics')
        col1, col2, col3, col4 = st.columns(4, gap='large')
        with col1:
            # Filtra a idade do entregador mais velho e mostra no dashboard
            #st.subheader('Idade do entregador mais velho')
            maior_idade = df1.loc[:, 'Delivery_person_Age'].max()
            col1.metric(label = 'Maior Idade:', value = maior_idade )
                        
        with col2:
            # Filtra a idade do entregador mais velho e mostra no dashboard
            #st.subheader('Idade do entregador mais novo')
            menor_idade = df1.loc[:, 'Delivery_person_Age'].min()
            col2.metric('Menor Idade:', menor_idade )
            
        with col3:
            #st.subheader('Melhor condição dos veículos')
            melhor_condicao = df1.loc[:, 'Vehicle_condition'].max()
            col3.metric('Melhor Condição:', melhor_condicao)
        with col4:
            #st.subheader('Pior condição dos veículos')                
            pior_condicao = df1.loc[:, 'Vehicle_condition'].min()
            col4.metric('Pior Condição:', pior_condicao)
    # bloco #2 de informação
    with st.container():
        st.markdown("""___""")
        st.title('Avaliações')
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('##### Avaliações médias por Entregador')
            colunas = ['Delivery_person_Ratings', 'Delivery_person_ID']
            df_avg_rating_per_deliver = (df1.loc[:, colunas]
                                             .groupby(['Delivery_person_ID'])
                                             .mean()
                                             .reset_index())
            st.dataframe(df_avg_rating_per_deliver)
        with col2:
            st.markdown('##### Avaliação média por trânsito')
            colunas = ['Delivery_person_Ratings', 'Road_traffic_density']
            df_rating_per_traffic = (df1.loc[:, colunas]
                                         .groupby(['Road_traffic_density'])
                                         .agg({'Delivery_person_Ratings': ['mean', 'std']}))
            df_rating_per_traffic.columns = ['delivery_mean', 'delivery_std']
            df_rating_per_traffic.reset_index()
            st.dataframe(df_rating_per_traffic)
            
            
            st.markdown('##### Avaliação média por clima')
            colunas = ['Delivery_person_Ratings', 'Weatherconditions']
            df_rating_per_weather = (df1.loc[:, colunas]
                                         .groupby(['Weatherconditions'])
                                         .agg({'Delivery_person_Ratings': ['mean', 'std']}))
            
            df_rating_per_weather.columns = ['delivery_mean', 'delivery_std']
            df_rating_per_weather.reset_index()
            st.dataframe(df_rating_per_weather)
        
    # bloco #3 de informação
    with st.container():
        st.markdown("""___""")
        
        #st.markdown(""" <style> div[data-testid="stVerticalBlock"] div[style*="flex-direction: column;"] div[data-testid="stVerticalBlock"] {border: 1px solid black;} </style>""", unsafe_allow_html=True)

        st.title ('Velocidade de Entrega')
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('##### TOP entregadores mais rápidos')
            colunas = ['Delivery_person_ID', 'City', 'Time_taken(min)']
            df_aux = (df1.loc[:, colunas]
                          .groupby(['City', 'Delivery_person_ID'])
                          .mean()
                          .sort_values(by=['City', 'Time_taken(min)'], ascending=True)
                          .reset_index())
            df_aux01 = df_aux.loc[df_aux['City'] == 'Metropolitian ',:].head(10)
            df_aux02 = df_aux.loc[df_aux['City'] == 'Urban ',:].head(10)
            df_aux03 = df_aux.loc[df_aux['City'] == 'Semi-Urban ',:].head(10)
            df_aux = pd.concat([df_aux01, df_aux02, df_aux03]).reset_index(drop=True)            
            st.dataframe(df_aux)
            
        with col2:
            st.markdown('##### TOP entregadores mais lentos')
            colunas = ['Delivery_person_ID', 'City', 'Time_taken(min)']
            df_aux = (df1.loc[:, colunas]
                          .groupby(['City', 'Delivery_person_ID'])
                          .mean()
                          .sort_values(by=['City', 'Time_taken(min)'], ascending=False)
                          .reset_index())
            df_aux01 = df_aux.loc[df_aux['City'] == 'Metropolitian ',:].head(10)
            df_aux02 = df_aux.loc[df_aux['City'] == 'Urban ',:].head(10)
            df_aux03 = df_aux.loc[df_aux['City'] == 'Semi-Urban ',:].head(10)
            df_aux = pd.concat([df_aux01, df_aux02, df_aux03]).reset_index(drop=True)        
            st.dataframe(df_aux)
        
        
        
        
        
        
        
        