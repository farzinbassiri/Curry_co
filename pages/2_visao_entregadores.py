
# Carregando os dados e fazendo limpeza inicial

# bibliotecas necessárias
import pandas as pd
import streamlit as st
from PIL import Image
from streamlit_folium import folium_static
from datetime import datetime, timedelta

st.set_page_config(page_title= 'Visão Entregadores', layout='wide')
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


st.header('Marketplace - Visão Cliente')

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


tab1, tab2 = st.tabs(['Visão Gerencial', 'Análises'])

# separa os códigos para cada aba
# todo código que estiber em 'with tab1 vai aparecer naquela aba
with tab1:
    # bloco #1 de informação
    with st.container():
        with st.container():
            sub_col1, sub_col2, sub_col3, sub_col4, sub_col5, sub_col6 = st.columns(6)
            with sub_col3:
                st.markdown('### Métricas Gerais')
        
        
        col1, col2, col3, col4, col5 = st.columns(5, gap='large')
        with col1:
            with st.container():
                # Filtra a idade do entregador mais velho e mostra no dashboard
                maior_idade = df1.loc[:, 'Delivery_person_Age'].max()
                texto = 'Idade do entregador mais velho [anos]:'
                col1.info(texto)
            with st.container():
                sub_col1, sub_col2, sub_col3 = st.columns(3)
                with sub_col2:
                    sub_col2.title(maior_idade)
                        
        with col2:
            # Filtra a idade do entregador mais velho e mostra no dashboard
            with st.container():
                # Filtra a idade do entregador mais velho e mostra no dashboard
                menor_idade = df1.loc[:, 'Delivery_person_Age'].min()
                texto = 'Idade do entregador mais novo [anos]:'
                col2.info(texto)
            with st.container():
                sub_col1, sub_col2, sub_col3 = st.columns(3)
                with sub_col2:
                    sub_col2.title(menor_idade)            
            
        with col3:
            with st.container():
                # Filtra a idade do entregador mais velho e mostra no dashboard
                melhor_condicao = df1.loc[:, 'Vehicle_condition'].max()
                texto = 'Melhor índice de conservação do veículo:'
                col3.info(texto)
            with st.container():
                sub_col1, sub_col2, sub_col3, sub_col4, sub_col5 = st.columns(5)
                with sub_col3:
                    #col6.metric(label = '', value = maior_idade )
                    sub_col3.title(melhor_condicao)                   
            
            
        with col4:
            #st.subheader('Pior condição dos veículos')                
            with st.container():
                # Filtra a idade do entregador mais velho e mostra no dashboard
                pior_condicao = df1.loc[:, 'Vehicle_condition'].min()
                texto = 'Pior índice de conservação do veículo:'
                col4.info(texto)
            with st.container():
                sub_col1, sub_col2, sub_col3, sub_col4, sub_col5 = st.columns(5)
                with sub_col3:
                    #col6.metric(label = '', value = maior_idade )
                    sub_col3.title(pior_condicao)     
                   
        with col5:
            col5.info('Quantidade de Dados após aplicação dos filtros:')
            sub_col1, sub_col2, sub_col3, sub_col4 = st.columns(4)
            with sub_col2:            
                sub_col2.title(len(df1))
            
                
    # bloco #2 de informação
    with st.container():
        st.markdown("""___""")
        col1, col2, col3, col4 = st.columns(4)
        with col2:
            st.markdown('### Métricas dos Entregadores')
            
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('##### Avaliações médias por Entregador')
            colunas = ['Delivery_person_Ratings', 'Delivery_person_ID']
            df_avg_rating_per_deliver = (df1.loc[:, colunas]
                                             .groupby(['Delivery_person_ID'])
                                             .mean()
                                             .round(1)
                                             .sort_values('Delivery_person_Ratings', ascending=False)
                                             .reset_index())
            st.dataframe(df_avg_rating_per_deliver, 400, 490)
        with col2:
            st.markdown('##### Avaliação média por trânsito')
            colunas = ['Delivery_person_Ratings', 'Road_traffic_density']
            df_rating_per_traffic = (df1.loc[:, colunas]
                                         .groupby(['Road_traffic_density'])
                                         .agg({'Delivery_person_Ratings': ['mean', 'std']}).round(1))
            df_rating_per_traffic.columns = ['delivery_mean', 'delivery_std']
            df_rating_per_traffic = df_rating_per_traffic.sort_values('delivery_mean', ascending=False)
            st.dataframe(df_rating_per_traffic)
            
            
            st.markdown('##### Avaliação média por clima')
            colunas = ['Delivery_person_Ratings', 'Weatherconditions']
            df_rating_per_weather = (df1.loc[:, colunas]
                                         .groupby(['Weatherconditions'])
                                         .agg({'Delivery_person_Ratings': ['mean', 'std']}).round(1))
            
            df_rating_per_weather.columns = ['delivery_mean', 'delivery_std']
            df_rating_per_weather = df_rating_per_weather.sort_values('delivery_mean', ascending=False)
            st.dataframe(df_rating_per_weather)
        
    # bloco #3 de informação
    with st.container():
        st.markdown("""___""")

        sub_col1, sub_col2, sub_col3, sub_col4 = st.columns(4)
        with sub_col2:
            st.markdown('### Velocidade de Entrega')
        #st.title ('Velocidade de Entrega')
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('##### TOP entregadores mais rápidos')
            colunas = ['Delivery_person_ID', 'City', 'Time_taken(min)']
            df_aux = (df1.loc[:, colunas]
                          .groupby(['City', 'Delivery_person_ID'])
                          .mean()
                          .round(1)
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
                          .round(1)
                          .sort_values(by=['City', 'Time_taken(min)'], ascending=False)
                          .reset_index())
            df_aux01 = df_aux.loc[df_aux['City'] == 'Metropolitian ',:].head(10)
            df_aux02 = df_aux.loc[df_aux['City'] == 'Urban ',:].head(10)
            df_aux03 = df_aux.loc[df_aux['City'] == 'Semi-Urban ',:].head(10)
            df_aux = pd.concat([df_aux01, df_aux02, df_aux03]).reset_index(drop=True)        
            st.dataframe(df_aux)
        
        
        
with tab2:
    with st.container():
        col1, col2 = st.columns(2, gap='large')
        with col1:
            fig = grafico_entregas(df1, True, 'Delivery_person_Age', 'Idade dos entregadores', '% de ocorrências', 'Idade dos Entregadores')
            st.plotly_chart(fig, use_container_width = True)  
        with col2:
            fig = grafico_entregas(df1, False, 'Delivery_person_Age', 'Idade dos entregadores', '% de ocorrências', 'Idade dos Entregadores')
            st.plotly_chart(fig, use_container_width = True)  

    with st.container():
        col1, col2, col3 = st.columns(3)
        with col2:
            col2.info('Quantidade de Dados após aplicação dos filtros:')
            sub_col1, sub_col2, sub_col3, sub_col4, sub_col5 = st.columns(5)
            with sub_col3:            
                sub_col3.title(len(df1))
        
        