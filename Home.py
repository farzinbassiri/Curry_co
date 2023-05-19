import streamlit as st
from PIL import Image

st.set_page_config(page_title="Home", layout='wide')
image = Image.open('logo.jpg')

st.sidebar.image(image, width = 120)
st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""___""")

st.write("# Curry Company Growth Dashboard")

st.markdown(
""" Growth Dashboard foi contruido para acompanhar as métricas de crescimento dos entregadores e restaurantes.
    ### Como utilizar esse Growth Dashboard?
    - Visão empresa:
        - Visão gerencial: métricas gerais de comportamento.
        - Visão Tática: indicadores semanais de crescimento.
        - Visão Geográfica: Insights de geolocalização.
    - Visão entregador:
        - Acompanhamento dos indicadores semanais de crescimento
    - Visão restaurante: 
        -Indicadores semanais de crescimento dos restaurantes

    ### Ask for help
        - time de Data Science no Discord
            - @username

""")