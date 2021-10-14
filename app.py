import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import networkx as nx
from pyvis.network import Network
from htbuilder import HtmlElement, div, hr, a, p, img, styles
from htbuilder.units import percent, px
from operator import itemgetter

def footer_image(src_as_string, **style):
    return img(src=src_as_string, style=styles(**style))

def link(link, text, **style):
    return a(_href=link, _target="_blank", style=styles(**style))(text)

def layout(*args):

    style = """
    <style>
      # MainMenu {visibility: hidden;}
      footer {visibility: hidden;}
    </style>
    """

    style_div = styles(
        left=0,
        bottom=0,
        margin=px(0, 0, 0, 0),
        width=percent(100),
        text_align="center",
        height="0px",
        opacity=0.7
    )

    style_hr = styles(
        display="block",
        margin=px(8, 8, 8, 8),
        border_style="inset",
        border_width=px(1)
    )

    body = p()
    foot = div(style=style_div)(hr(style=style_hr), body)

    st.markdown(style, unsafe_allow_html=True)

    for arg in args:
        if isinstance(arg, str):
            body(arg)
        elif isinstance(arg, HtmlElement):
            body(arg)

    st.markdown(str(foot), unsafe_allow_html=True)

def footer():
    myargs = [
        "Developed using Python ",
        link("https://www.python.org/", footer_image('https://i.imgur.com/ml09ccU.png',
        	width=px(18), height=px(18), margin= "0em")),
        " , Networkx ",
        link("https://networkx.org/", footer_image('https://avatars.githubusercontent.com/u/388785?s=200&v=4',
        	width=px(18), height=px(18), margin= "0em")),
        " and Streamlit ",
        link("https://streamlit.io/", footer_image('https://pbs.twimg.com/profile_images/1366779897423810562/kn7ucNPv.png',
        	width=px(18), height=px(18), margin= "0em")),
        " . For more details about the project, please visit this ",
        link("https://github.com/dfmaz/EII-GraphModel", "Github repo"),
        "<br><b>2021 | Daniel Fernández Martínez ",
        link("https://dfmaz.github.io/", footer_image('https://github.com/dfmaz/dfmaz.github.io/blob/main/img/favicon.png?raw=true',
        	width=px(24), height=px(24), margin= "0em")),
    ]
    layout(*myargs)

def short_name(grafo):
    new_nodes = []
    for node in grafo.nodes():
        new_nodes.append(node.split(' ')[0])
        
    mapping = dict(zip(grafo.nodes(), new_nodes))
        
    grafo = nx.relabel_nodes(grafo, mapping)
    
    return grafo

def main():
    df_electrica = pd.read_csv('data/electrica.csv')
    df_electronica = pd.read_csv('data/electronica.csv')
    df_mecanica = pd.read_csv('data/mecanica.csv')
    df_industrial = pd.read_csv('data/industrial.csv')

    electrica = short_name(nx.complete_graph(df_electrica['Empresa'].values.tolist()))
    electronica = short_name(nx.complete_graph(df_electronica['Empresa'].values.tolist()))
    mecanica = short_name(nx.complete_graph(df_mecanica['Empresa'].values.tolist()))
    industrial = short_name(nx.complete_graph(df_industrial['Empresa'].values.tolist()))

    st.set_page_config(page_title='EIIGraph',
                    layout='wide')

    st.markdown('## **EIIGraph**: An Interactive Graph Model Visualization of the Collaborating Companies Network of the Industrial Engineering School from the University of Extremadura, Spain')
    st.markdown('### _A collaborating company is understood as one having an **internship** agreement with the School. The nodes of the network are made up by the own companies and they will be connected to each other if they admit students of the same degree._')

    c1, c2 = st.columns((1,3))
    with c1:
        list_degrees = ["BSc. Electrical", "BSc. Electronics", "BSc. Mechanical", "MSc. Industrial"]
        dictio = {"BSc. Electrical": electrica, "BSc. Electronics": electronica, "BSc. Mechanical": mecanica, "MSc. Industrial": industrial}

        st.markdown('#### ')
        st.markdown('#### Select degree(s) to visualize')
        selected_degrees = st.multiselect('', list_degrees)

        if len(selected_degrees) == 0:
            st.markdown('###### Choose at least 1 degree to start')

        else:
            seleccion = []
            for i in selected_degrees:
                seleccion.append(dictio[i])

            G = nx.compose_all(seleccion)
            G.name = selected_degrees

            st.markdown('#### Network info')
            st.text(nx.info(G))
            
            st.markdown('#### TOP 10 Nodes :star:')
            degree_dict = dict(G.degree(G.nodes()))
            sorted_degree = sorted(degree_dict.items(), key=itemgetter(1), reverse=True)
            df_info = pd.DataFrame(sorted_degree[:10], columns=['Company', 'Degree'])
            df_info = df_info.set_index('Company')
            st.dataframe(df_info)

            eii_net = Network(
                            height='550px',
                            width='100%',
                            bgcolor='#333333',
                            font_color='white'
                            )

    with c2:
        if len(selected_degrees) == 0:
            st.markdown('######')
            st.markdown('#### Nothing to show... :hourglass_flowing_sand:')

        else:
            st.markdown('######')
            st.markdown('#### Graph visualization :mag_right:')

            eii_net.from_nx(G)
            eii_net.repulsion(
                                node_distance=420,
                                central_gravity=0.33,
                                spring_length=500,
                                spring_strength=0.10,
                                damping=0.95,
                            )
            try:
                path = '/tmp'
                eii_net.save_graph(f'{path}/eii_network_graph.html')
                HtmlFile = open(f'{path}/eii_network_graph.html', 'r', encoding='utf-8')

            except:
                path = 'html_files'
                eii_net.save_graph(f'{path}/eii_network_graph.html')
                HtmlFile = open(f'{path}/eii_network_graph.html', 'r', encoding='utf-8')

            components.html(HtmlFile.read(), height=600)

    footer()

if __name__ == "__main__":
    main()
