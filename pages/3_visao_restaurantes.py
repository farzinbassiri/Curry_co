
# Carregando os dados e fazendo limpeza inicial

# bibliotecas necessárias
import pandas as pd
import streamlit as st
from PIL import Image
from streamlit_folium import folium_static
from datetime import datetime, timedelta

st.set_page_config(page_title= 'Visão Restaurantes', layout='wide')
# lendo o arquivo importado

# lendo o arquivo com os dados a serem importados
df = pd.read_csv('Dataset\\train.csv')

# importa o módulo de tratamento dos dados
# esse módulo é formado por um conjunto de funções que fazem a limpeza dos dados
from data_wrangling_modules import *

# chama a função que faz a limpeza geral dos dados coletados.

df1 = limpa_dados(df)


#--------------------------------------------------------------
#                    Barra Lateral    
#--------------------------------------------------------------


st.header('Marketplace - Visão Restaurantes')

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


tab1, tab2, tab3 = st.tabs(['Visão Gerencial', 'Análises', '-'])

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
            with st.container():
                delivery_unique = len(df1.loc[:,'Delivery_person_ID'].unique())
                texto = 'Número de Entregadores Cadastrados'
                col1.info(texto)
            with st.container():
                sub_col1, sub_col2, sub_col3 = st.columns(3)
                with sub_col2:
                    sub_col2.title(delivery_unique)

        # monta as colunas de interesse no filtro
        with col2:
            df_mean = deslocamento_medio(df1)
            with st.container():
                col2.info('Distância Média das Entregas [km]')
            with st.container():
                sub_col1, sub_col2, sub_col3 = st.columns(3)
                with sub_col2:
                    sub_col2.title(df_mean)            
            
        with col3:
            df_mean = tempo_entrega(df1, 'media', True)
            with st.container():
                col3.info('Tempo médio de entrega com festival [min]')  
            with st.container():
                sub_col1, sub_col2, sub_col3 = st.columns(3)
                with sub_col2:
                    sub_col2.title(df_mean)            
                        
            
        with col4:
            df_std = tempo_entrega(df1, 'std', True)
            with st.container():
                col4.info('Desvio padrão do Tempo de entrega com festival [min]')  
            with st.container():
                sub_col1, sub_col2, sub_col3 = st.columns(3)
                with sub_col2:
                    sub_col2.title(df_std)            
            
        with col5:
            df_mean = tempo_entrega(df1, 'media', False)
            with st.container():
                col5.info('Tempo médio de entrega sem festival [min]')  
            with st.container():
                sub_col1, sub_col2, sub_col3 = st.columns(3)
                with sub_col2:
                    sub_col2.title(df_mean)     

        with col6:
            df_std = tempo_entrega(df1, 'std', False)
            with st.container():
                col6.info('Desvio padrão do Tempo de entrega sem festival [min]')  
            with st.container():
                sub_col1, sub_col2, sub_col3 = st.columns(3)
                with sub_col2:
                    sub_col2.title(df_std)     


            
    with st.container():
        fig = grafico_tempo_medio_entrega(df1)
        st.plotly_chart(fig)
        st.markdown("""___""")


with tab2:
    col1, col2 = st.columns(2, gap='large')
    with col1:
        fig = grafico_entregas(df1, True, 'Time_taken(min)', 'Tempo de Entrega [min]', '% de ocorrências', 'Tempo de Entrega')
        st.plotly_chart(fig, use_container_width = True)  
    with col2:
        fig = grafico_entregas(df1, False, 'Time_taken(min)', 'Tempo de Entrega [min]', '% de ocorrências', 'Tempo de Entrega')
        st.plotly_chart(fig, use_container_width = True)  
        
        
    st.markdown("""___""")   