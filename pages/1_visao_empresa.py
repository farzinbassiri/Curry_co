
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

st.set_page_config(page_title= 'Visão Empresa', layout='wide')

# lendo o arquivo importado
df = pd.read_csv('dataset\\train.csv')
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

st.header('Marketplace - Visão Cliente')

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
    with st.container():
        st.markdown('# Orders by Day')
        cols =  ['ID', 'Order_Date']
        df_aux = df1.loc[:, cols].groupby( 'Order_Date' ).count().reset_index()
        # altera o nome da coluna ID
        df_aux.columns = ['order_date', 'qtde_entregas']

        # gráfico
        fig = px.bar( df_aux, x='order_date', y='qtde_entregas', range_y= [0,1200])
        st.plotly_chart(fig, use_conteiner_width = True)
    
    # criando mais duas colunas no dashboard
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            st.header('Traffic Order Share')
            df_aux = df1.loc[:, ['ID', 'Road_traffic_density']].groupby( 'Road_traffic_density' ).count().reset_index()
            df_aux['perc_ID'] = 100 * ( df_aux['ID'] / df_aux['ID'].sum() )
            # gráfico
            #fig = px.pie( df_aux, values='perc_ID', names='Road_traffic_density' )
            fig = px.bar( df_aux, x='Road_traffic_density', y = 'perc_ID')
            st.plotly_chart(fig, use_conteiner_width = True)
            
        with col2:
            st.header('Traffic Order City')
            df_aux = df1.loc[:, ['ID', 'City', 'Road_traffic_density']].groupby(['City', 'Road_traffic_density']).count().reset_index()
            fig = px.scatter(df_aux, x= 'City', y= 'Road_traffic_density', size = 'ID', color = 'City')
            st.plotly_chart(fig, use_conteiner_width = True)
            
    
    
with tab2:
    st.markdown('# Order by Week')
    
    df1['week_of_year'] = df1['Order_Date'].dt.strftime( "%U" )
    df_aux = df1.loc[:, ['ID', 'week_of_year']].groupby( 'week_of_year' ).count().reset_index()
    # gráfico
    fig = px.bar( df_aux, x='week_of_year', y='ID' )    
    st.plotly_chart(fig, use_conteiner_width = True)
with tab3:
    st.markdown('# Country Map')

    data_plot = df1.loc[:, ['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']].\
                groupby( ['City','Road_traffic_density']).median().reset_index()
    #print(data_plot.head(5))


    # Desenhar o mapa
    mapa = folium.Map(height=300, width=500, zoom_start=20)
    for index, location_info in data_plot.iterrows():
        folium.Marker( [location_info['Delivery_location_latitude'],
                        location_info['Delivery_location_longitude']],
                        popup=location_info[['City', 'Road_traffic_density']] ).add_to( mapa )
    folium_static(mapa, width = 1024, height = 600)
    