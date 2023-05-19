# importa as bibliotecas
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
#from screeninfo import get_monitors
import folium
from haversine import haversine
import numpy as np
import math

"""
Funções de limpeza de dados:

-----------------------------------------------------------------------------------------------
    - limpa_vazios(df1, conteudo_invalido, coluna):

        # função para eliminar linhas que contém conteúdo inválido
            # entradas:
                # dataframe com os dados a serem limpos
                # conteudo a ser eliminado -->  texto
                # coluna a ser limpa --> texto
            # saídas:
                # dataframe com a coluna convertida

-----------------------------------------------------------------------------------------------
    - transforma_tipo(df1, novo_tipo, coluna):

        # função para transformar typo de dados nas colunas
            # entradas:
                # dataframe com os dados a serem limpos
                # qual o novo tipo de dados da coluna (int, float, etc...)
                # coluna a ter o tipo de dado transformado
            # saídas:
                # dataframe com a coluna convertida

-----------------------------------------------------------------------------------------------
    - limpa_dados(df1):
    
        # realiza usa as funções anteriores para fazer a limpeza e transformação dos dados

-----------------------------------------------------------------------------------------------

    - grafico_barras(df1, cols, group_by_col, x_axis, y_axis, x_label, y_label, graph_label):

        # função para criar gráfico de barras
            # entradas:
                # dataframe com os dados a serem limpos
                # colunas que serão colocadas no gráfico
                # indicação de qual coluna é o eixo 'x' e qual é o eixo 'y'
                # indicação dos nomes dos eixos
                # indicação do nome do gráfico
            # saídas:
                # dataframe com a coluna convertida

-----------------------------------------------------------------------------------------------
"""


def limpa_vazios(df1, conteudo_invalido, coluna):
    linhas_validas = df1[coluna] != conteudo_invalido
    #transfere para o dataframe apenas as linhas que contém dados
    df1 = df1.loc[linhas_validas, :]
    # refaz o index depois de remover as linhas inválidas
    df1 = df1.reset_index(drop = True)
    return df1

    

def transforma_tipo(df1, novo_tipo, coluna):
    # transforma a variável para o novo tipo.
    df1[coluna] = df1[coluna].astype(novo_tipo)
    return df1



def limpa_dados(df1):
    # eliminando espaços no final de duas colunas
    df1.loc[:, 'ID'] = df1.loc[:, 'ID'].str.strip()
    df1.loc[:, 'Delivery_person_ID'] = df1.loc[:, 'Delivery_person_ID'].str.strip()
    df1.loc[:, 'Festival'] = df1.loc[:, 'Festival'].str.strip()
    df1.loc[:, 'Weatherconditions'] = df1.loc[:, 'Weatherconditions'].str.strip('conditions ')

    # primeiro precisa excluir valores faltantes preenchidos com texto:'NaN ' - houve erro ao converter indicando essa necessidade
    df1 = limpa_vazios(df1, 'NaN ', 'Delivery_person_Age')
    df1 = limpa_vazios(df1, 'NaN ', 'Delivery_person_Ratings')
    df1 = limpa_vazios(df1, 'NaN ', 'multiple_deliveries')
    df1 = limpa_vazios(df1, 'conditions NaN', 'Weatherconditions')
    df1 = limpa_vazios(df1, 'NaN', 'Weatherconditions')
    df1 = limpa_vazios(df1, 'NaN ', 'Road_traffic_density')
    df1 = limpa_vazios(df1, 'NaN ', 'City')
    df1 = limpa_vazios(df1, 'NaN ', 'Festival')
    df1 = limpa_vazios(df1, 'NaN', 'Festival')

    df1 = transforma_tipo(df1, int, 'Delivery_person_Age')
    df1 = transforma_tipo(df1, int, 'multiple_deliveries')
    df1 = transforma_tipo(df1, float, 'Delivery_person_Ratings')

    # transforma coluna de datas para o formato de data
    df1['Order_Date'] = pd.to_datetime( df1['Order_Date'], format='%d-%m-%Y' )

    # Comando para remover o texto de números
    df1.loc[:, 'Time_taken(min)'] = df1.loc[:, 'Time_taken(min)'].str.strip('(min) ')
    df1 = transforma_tipo(df1, int, 'Time_taken(min)')

    df1.loc[:,'Road_traffic_density'] = df1.loc[:, 'Road_traffic_density'].str.strip()
    #print('Limpeza dos dados realizada com sucesso!')
    return df1



def grafico_order_date(df1):

    cols= ['ID', 'Order_Date']
    group_by_col= 'Order_Date' 
    x_axis = 'order_date'
    y_axis = 'qtde_entregas'
    x_label = 'Data do Pedido'
    y_label = 'Quantidade de Entregas'
    graph_label = 'Quantidade de Entregas Realizadas'
    
    # detecta a resolução do monitor para definir o tamanho do gráfico
    #max_width= get_monitors()[0].width
    #max_height= get_monitors()[0].height
    max_width = st.get_container_width
    max_height = st.get_container_height
    
    df_aux = df1.loc[:, cols].groupby(group_by_col).count().reset_index()
    # altera o nome da coluna ID
    df_aux.columns = [x_axis, y_axis]

    # define a escala do gráfico, coloca o ponto de máximo do eixo em 20% acima do valor máximo a ser exibido
    graph_range = df_aux[y_axis].max()*1.2
    # gráfico
    fig = px.bar(df_aux, 
                 x=x_axis, 
                 y=y_axis, 
                 range_y= [0,graph_range], 
                 labels={ x_axis: x_label, y_axis: y_label},
                 title=graph_label,
                 width=int(max_width*0.7),
                 height=int(max_height*0.4))

    # configura o título do gráfico
    # title_x --> alinhamento central;  
    # Se < 0.5 --> desloca à esquerda
    # Se > 0.5 --> desloca à direita
    fig.update_layout(
            title_font = {"size": 40},
            font_family="Arial",
            font_color="Black",
            title_font_family="Arial",
            title_font_color="black",
            title_x=0.25)
    # configura os títulos dos eixos
    fig.update_xaxes(
            tickangle = 0,
            title_text = x_label,
            title_font = {"size": 22},
            tickfont_size=18)

    fig.update_yaxes(
            title_text = y_label,
            title_font = {"size": 22},
            tickfont_size=18)    
    return fig




def grafico_road_traffic(df1):
    cols= ['ID', 'Road_traffic_density']
    group_by_col= 'Road_traffic_density' 
    x_axis = 'Road_traffic_density'
    y_axis = 'perc_ID'
    x_label = 'Condição do tráfego durante a entrega'
    y_label = '% das entregas'
    graph_label = 'Distribuição das entregas'
    
    
    df_aux = df1.loc[:, cols].groupby(group_by_col).count().reset_index()
    #cria coluna adicional com a proporcionalidade de cada consição de trafego e ordena pelo que quem mais contribuição (formato proximo ao do Pareto)
    df_aux['perc_ID'] = 100 * ( df_aux['ID'] / df_aux['ID'].sum() )
    df_aux = df_aux.sort_values(by='perc_ID', ascending=False)


    # controi o gráfico
    fig = px.bar(df_aux, 
                 x=x_axis, 
                 y=y_axis, 
                 labels={ x_axis: x_label, y_axis: y_label},
                 title=graph_label)

    # configura o título do gráfico
    # title_x --> alinhamento central;  
    # Se < 0.5 --> desloca à esquerda
    # Se > 0.5 --> desloca à direita
    fig.update_layout(
            title_font = {"size": 40},
            font_family="Arial",
            font_color="Black",
            title_font_family="Arial",
            title_font_color="black",
            title_x=0.2)
    # configura os títulos dos eixos
    fig.update_xaxes(
            tickangle = 0,
            title_text = x_label,
            title_font = {"size": 22},
            tickfont_size=18)

    fig.update_yaxes(
            title_text = y_label,
            title_font = {"size": 22},
            tickfont_size=18)    
    
    return fig


def grafico_city_traffic(df1):
    cols= ['ID', 'City', 'Road_traffic_density']
    group_by_col= ['City', 'Road_traffic_density'] 
    x_axis = 'City'
    y_axis = 'Road_traffic_density'
    x_label = 'Porte da Cidade'
    y_label = 'Tipo de Tráfego'
    graph_label = 'Porte das Cidades'
    color_map = 'City'
    size_map = 'ID'
  
    
    df_aux = df1.loc[:, cols].groupby(group_by_col).count().reset_index()
 
    # constroi o gráfico
    fig = px.scatter(df_aux, 
                     x= x_axis, 
                     y= y_axis, 
                     size = size_map, 
                     color = color_map,
                     labels={ x_axis: x_label, y_axis: y_label},
                     title=graph_label)
    

    # configura o título do gráfico
    # title_x --> alinhamento central;  
    # Se < 0.5 --> desloca à esquerda
    # Se > 0.5 --> desloca à direita
    fig.update_layout(
            title_font = {"size": 40},
            font_family="Arial",
            font_color="Black",
            title_font_family="Arial",
            title_font_color="black",
            title_x=0.2)
    # configura os títulos dos eixos
    fig.update_xaxes(
            tickangle = 0,
            title_text = x_label,
            title_font = {"size": 22},
            tickfont_size=18)

    fig.update_yaxes(
            title_text = y_label,
            title_font = {"size": 22},
            tickfont_size=18)    
    
    return fig


            

def grafico_road_traffic(df1):
    cols= ['ID', 'Road_traffic_density']
    group_by_col= 'Road_traffic_density' 
    x_axis = 'Road_traffic_density'
    y_axis = 'perc_ID'
    x_label = 'Condição do tráfego durante a entrega'
    y_label = '% das entregas'
    graph_label = 'Distribuição das entregas'
    
    
    df_aux = df1.loc[:, cols].groupby(group_by_col).count().reset_index()
    #cria coluna adicional com a proporcionalidade de cada consição de trafego e ordena pelo que quem mais contribuição (formato proximo ao do Pareto)
    df_aux['perc_ID'] = 100 * ( df_aux['ID'] / df_aux['ID'].sum() )
    df_aux = df_aux.sort_values(by='perc_ID', ascending=False)


    # controi o gráfico
    fig = px.bar(df_aux, 
                 x=x_axis, 
                 y=y_axis, 
                 labels={ x_axis: x_label, y_axis: y_label},
                 title=graph_label)

    # configura o título do gráfico
    # title_x --> alinhamento central;  
    # Se < 0.5 --> desloca à esquerda
    # Se > 0.5 --> desloca à direita
    fig.update_layout(
            title_font = {"size": 40},
            font_family="Arial",
            font_color="Black",
            title_font_family="Arial",
            title_font_color="black",
            title_x=0.2)
    # configura os títulos dos eixos
    fig.update_xaxes(
            tickangle = 0,
            title_text = x_label,
            title_font = {"size": 22},
            tickfont_size=18)

    fig.update_yaxes(
            title_text = y_label,
            title_font = {"size": 22},
            tickfont_size=18)    
    
    return fig


def grafico_weekly_order(df1):
    cols= ['ID', 'week_of_year']
    group_by_col= 'week_of_year'
    x_axis = 'week_of_year'
    y_axis = 'ID'
    x_label = 'Semana do Ano'
    y_label = 'Quantidade de Entregas'
    graph_label = 'Quantidade de Entregas Realizadas'
    


    df1['week_of_year'] = df1['Order_Date'].dt.strftime("%U")
    df_aux = df1.loc[:, cols].groupby(group_by_col).count().reset_index()

 

    
    # detecta a resolução do monitor para definir o tamanho do gráfico
#    max_width= get_monitors()[0].width
#    max_height= get_monitors()[0].height
    max_width = st.get_container_width
    max_height = st.get_container_height 
    
    df_aux = df1.loc[:, cols].groupby(group_by_col).count().reset_index()
    # altera o nome da coluna ID
    df_aux.columns = [x_axis, y_axis]

    # define a escala do gráfico, coloca o ponto de máximo do eixo em 20% acima do valor máximo a ser exibido
    graph_range = df_aux[y_axis].max()*1.2
    # gráfico
    fig = px.bar(df_aux, 
                 x=x_axis, 
                 y=y_axis, 
                 range_y= [0,graph_range], 
                 labels={ x_axis: x_label, y_axis: y_label},
                 title=graph_label,
                 width=int(max_width*0.7),
                 height=int(max_height*0.5))

    # configura o título do gráfico
    # title_x --> alinhamento central;  
    # Se < 0.5 --> desloca à esquerda
    # Se > 0.5 --> desloca à direita
    fig.update_layout(
            title_font = {"size": 40},
            font_family="Arial",
            font_color="Black",
            title_font_family="Arial",
            title_font_color="black",
            title_x=0.3)
    # configura os títulos dos eixos
    fig.update_xaxes(
            tickangle = 0,
            title_text = x_label,
            title_font = {"size": 22},
            tickfont_size=18)

    fig.update_yaxes(
            title_text = y_label,
            title_font = {"size": 22},
            tickfont_size=18)    

    return fig            
            

    
    
def grafico_country_map(df1):
    
    data_plot = (df1.loc[:, ['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']]
                    .groupby( ['City','Road_traffic_density']).median().reset_index())
    
    # faz a latitude e longitude média global das entrgas para usar como ponto central da visualização do mapa
    start_location = [df1.loc[:, 'Delivery_location_latitude'].median(), df1.loc[:,'Delivery_location_longitude'].median()]
    
    mapa = folium.Map(location= start_location, min_zoom = 0, zoom_start=5)
    #adiciona os pontos geográficos ao mapa
    for index, location_info in data_plot.iterrows():
        folium.Marker( [location_info['Delivery_location_latitude'],
                        location_info['Delivery_location_longitude']],
                        popup=location_info[['City', 'Road_traffic_density']] ).add_to(mapa)
    
    return mapa


def deslocamento_medio(df1):
    # calcula a distancia entre os pontos de partida (restaurante) e chagada (cliente)
    # usando a função 'haversine' que tem como entradas latitude e longitude de saida e de chegada, a saída é a distancia, por padrão é em km
    # axis=1 para indicar que as varáveis estão em forma de coluna
    colunas = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']
    df1['distance'] = df1.loc[:, colunas].apply(lambda x: 
                                          haversine(
                                              (x['Restaurant_latitude'], x['Restaurant_longitude']),
                                              (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1)

    df_mean = np.round(df1.loc[:,'distance'].mean(), 2)
    return df_mean


def tempo_entrega(df1, operacao, evento):
    if evento == True:
        linhas_selecionadas = df1['Festival']== 'Yes'
    else:
        linhas_selecionadas = df1['Festival']== 'No'
        
    if operacao == 'media':
        resultado = np.round(df1.loc[linhas_selecionadas, 'Time_taken(min)'].mean(),1)
    else:
        resultado = np.round(df1.loc[linhas_selecionadas, 'Time_taken(min)'].std(),1)
    return resultado

def grafico_tempo_medio_entrega(df1):
        colunas = ['City', 'Time_taken(min)']
        df_mean = df1.loc[:, colunas].groupby('City').agg({'Time_taken(min)': ['mean', 'std']})
        df_mean.columns  = ['avg_time', 'std_time']
        df_mean = df_mean.reset_index()
        fig = go.Figure()
        fig.add_trace(go.Bar(name='Tempo Médio', x=df_mean['City'], y=df_mean['avg_time'], error_y=dict(type='data', array=df_mean['std_time'])))
        graph_label = 'Tempo médio de entrega por porte de cidade'
        fig.update_layout(
            title=graph_label,
            title_font = {"size": 40},
            font_family="Arial",
            font_color="Black",
            title_font_family="Arial",
            title_font_color="black",
            title_x=0.3)

        return fig

    
def grafico_entregas(df1, evento, cols, x_label, y_label, graph_label):

    # cols= coluna que irá gerar o histograma --> era 'Time_taken(min)'
    #group_by_col= 'week_of_year'
    #x_axis = 'Tempo de Entrega [min]'
    #y_axis = 'ID'
    #x_label = nome do eixo x --> 'Tempo de Entrega [min]'
    #y_label = nome do eixo y -->'% de ocorrências'
    #graph_label = 'Quantidade de Entregas Realizadas'
        
    
    
    
    if evento == True:
        linhas_selecionadas = df1['Festival']== 'Yes'
        texto = graph_label + ' durante Festival'
    else:
        linhas_selecionadas = df1['Festival']== 'No'
        texto = graph_label + ' sem Festival'
                
    #nbins_slider
    nbins_slider = int(1 + 3.322 * math.log(len(df1)))
    #histnorm = 'percent', 'probability', 'density', 'probability density'
    fig = px.histogram(df1.loc[linhas_selecionadas, :], 
                       x = cols,
                       nbins = nbins_slider,
                       title = texto,
                       histnorm = 'percent')
    fig.update_layout(bargap=0.2)

    fig.update_layout(
            title_font = {"size": 20},
            font_family="Arial",
            font_color="Black",
            title_font_family="Arial",
            title_font_color="black",
            title_x=0.3)                
    # configura os títulos dos eixos
    fig.update_xaxes(
            tickangle = 0,
            title_text = x_label,
            title_font = {"size": 18},
            tickfont_size=18)

    fig.update_yaxes(
            title_text = y_label,
            title_font = {"size": 18},
            tickfont_size=18)   
    
    return fig