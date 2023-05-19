
# Carregando os dados e fazendo limpeza inicial

# bibliotecas necessárias
import pandas as pd
import streamlit as st
from PIL import Image
from streamlit_folium import folium_static
from datetime import datetime, timedelta

st.set_page_config(page_title= 'Visão Empresa', layout='wide')


# lendo o arquivo com os dados a serem importados
df = pd.read_csv('train.csv')

# importa o módulo de tratamento dos dados
# esse módulo é formado por um conjunto de funções que fazem a limpeza dos dados
from data_wrangling_modules import *

# chama a função que faz a limpeza geral dos dados coletados.

df1 = limpa_dados(df)



#--------------------------------------------------------------
#                    Barra Lateral    
#--------------------------------------------------------------


st.header('Marketplace - Visão Empresa')

image = Image.open('logo.jpg')
st.sidebar.image(image, width=120)

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""___""")
st.sidebar.markdown('## Selecione uma data limite')

# seleção da data de interesse pelo usuário


data_inicial= df1['Order_Date'].min()
data_final= df1['Order_Date'].max()

date_slider = st.sidebar.slider(
                   'Defina o intervalo com as datas desejadas:',
                    min_value = datetime(data_inicial.year, data_inicial.month, data_inicial.day),
                    max_value = datetime(data_final.year, data_final.month, data_final.day),
                    value = datetime(data_final.year, data_final.month, data_final.day),
                    format = 'DD-MM-YYYY')

st.sidebar.markdown("""___""")

# seleção da condição de transito 
traffic_options = st.sidebar.multiselect(
                        'Quais as condições do trânsito?',
                        ['Low', 'Medium', 'High', 'Jam'],
                        default = ['Low', 'Medium', 'High', 'Jam'])


# seleção do porte de cidade
city_options = st.sidebar.multiselect(
                        'Quais os portes de cidade?',
                        ['Metropolitian ', 'Semi-Urban ', 'Urban '],
                        default = ['Metropolitian ', 'Semi-Urban ', 'Urban '])

st.sidebar.markdown("""___""")
st.sidebar.markdown('###### Powered by Comunidade DS')


# aplica os filtros do sidebar na tabela de dados

# filtro de data
linhas_selecionadas = df1['Order_Date'] < date_slider 
df1 = df1.loc[linhas_selecionadas,:]

#filtro de transito
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas,:]

#filtro de porte de cidade
linhas_selecionadas = df1['City'].isin(city_options)
df1 = df1.loc[linhas_selecionadas,:]
#--------------------------------------------------------------
#           Layout do dashboard - usando streamlit    
#--------------------------------------------------------------

#Abas com as diferentes métricas 

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

# separa os códigos para cada aba
# todo código que estiber em 'with tab1 vai aparecer naquela aba

with tab1: # 'Visão Gerencial'
    with st.container():
        #monta o gráfico com a quantidade de entregas realizadas a cada dia
        fig = grafico_order_date(df1)
        st.plotly_chart(fig, use_conteiner_width = True)
        
    # criando mais duas colunas no dashboard
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            #monta o gráfico com a distribuição das entregas por tipo de tráfego
            fig = grafico_road_traffic(df1)
            st.plotly_chart(fig, use_conteiner_width = True)
            
        with col2:
            #monta o gráfico com a distribuição das entregas por porte de cidade e tipo de tráfego
            fig = grafico_city_traffic(df1)
            st.plotly_chart(fig, use_conteiner_width = True)
            
    
    
with tab2:
    #monta o gráfico com a distribuição das entregas por semana do ano
    fig = grafico_weekly_order(df1)
    st.plotly_chart(fig, use_conteiner_width = True)
    
with tab3:
    st.markdown('# Pontos Centrais das Entregas')
    mapa = grafico_country_map(df1)

#    max_width= get_monitors()[0].width * 0.7
#    max_height= get_monitors()[0].height * 0.7
    max_width = 1980 * 0.7
    max_height = 1080 * 0.7    
    folium_static(mapa, width = max_width, height = max_height)

    