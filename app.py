import streamlit as st
import pandas as pd
import psycopg2
import plotly.express as px

# ------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA
# ------------------------------------------------

st.set_page_config(
    page_title="Dashboard Financeiro",
    layout="wide"
)

# ------------------------------------------------
# LOGIN
# ------------------------------------------------

USUARIO = "admin"
SENHA = "1086"

if "logado" not in st.session_state:
    st.session_state.logado = False

def tela_login():

    st.title("Login - Dashboard Financeiro")

    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):

        if usuario == USUARIO and senha == SENHA:
            st.session_state.logado = True
            st.rerun()
        else:
            st.error("Usuário ou senha incorretos")

if not st.session_state.logado:
    tela_login()
    st.stop()

# ------------------------------------------------
# LOGOUT
# ------------------------------------------------

if st.sidebar.button("Logout"):
    st.session_state.logado = False
    st.rerun()

# ------------------------------------------------
# CONEXÃO BANCO
# ------------------------------------------------

conn = psycopg2.connect(
    host="localhost",
    database="datalab",
    user="postgres",
    password="8604",
    port="5432"
)

query = "SELECT * FROM financeiro"

df = pd.read_sql(query, conn)

# ------------------------------------------------
# TRATAMENTO DADOS
# ------------------------------------------------

df["periodo"] = pd.to_datetime(df["periodo"])

df["mes"] = df["periodo"].dt.to_period("M").astype(str)

# ------------------------------------------------
# TÍTULO
# ------------------------------------------------

st.title("Dashboard Financeiro")

# ------------------------------------------------
# FILTROS
# ------------------------------------------------

st.sidebar.header("Filtros")

meses = sorted(df["mes"].unique())

mes_selecionado = st.sidebar.selectbox(
    "Mês",
    meses
)

tipo_selecionado = st.sidebar.multiselect(
    "Tipo",
    df["tipo"].unique(),
    default=df["tipo"].unique()
)

df_mes = df[(df["mes"] == mes_selecionado) & (df["tipo"].isin(tipo_selecionado))]

# ------------------------------------------------
# VARIAÇÃO MÊS
# ------------------------------------------------

mes_anterior = str(pd.Period(mes_selecionado) - 1)

valor_atual = df_mes["valor"].sum()

valor_anterior = df[
    (df["mes"] == mes_anterior) &
    (df["tipo"].isin(tipo_selecionado))
]["valor"].sum()

if valor_anterior == 0:
    variacao = 0
else:
    variacao = (valor_atual - valor_anterior) / valor_anterior

# cor da variação
if variacao > 0:
    cor = "green"
elif variacao < 0:
    cor = "red"
else:
    cor = "black"

# ------------------------------------------------
# KPIs
# ------------------------------------------------

receita = df_mes[df_mes["tipo"] == "receita"]["valor"].sum()

despesa = df_mes[df_mes["tipo"] == "despesa"]["valor"].sum()

investimento = df_mes[df_mes["tipo"] == "investimento"]["valor"].sum()

saldo = receita - despesa

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric(
    "Receita",
    f"R$ {receita:,.2f}"
)

col2.metric(
    "Despesa",
    f"R$ {despesa:,.2f}"
)

col3.metric(
    "Investimento",
    f"R$ {investimento:,.2f}"
)

col4.metric(
    "Saldo",
    f"R$ {saldo:,.2f}"
)

col5.markdown(
    f"""
    <h4>Variação</h4>
    <h2 style='color:{cor}'>{variacao:.2%}</h2>
    """,
    unsafe_allow_html=True
)

# ------------------------------------------------
# TOP DESPESAS
# ------------------------------------------------

st.subheader("Top despesas")

top_despesas = df_mes[df_mes["tipo"] == "despesa"]

top_despesas = top_despesas.groupby("subcategoria")["valor"].sum().reset_index()

top_despesas = top_despesas.sort_values("valor", ascending=False)

fig1 = px.bar(
    top_despesas,
    x="subcategoria",
    y="valor",
    color="valor",
    color_continuous_scale="reds"
)

st.plotly_chart(fig1, use_container_width=True)

# ------------------------------------------------
# DESPESA POR CATEGORIA
# ------------------------------------------------

st.subheader("Despesas por categoria")

graf2 = df[df["tipo"] == "despesa"]

graf2 = graf2.groupby("categoria")["valor"].sum().reset_index()

graf2 = graf2.sort_values("valor", ascending=False)

fig2 = px.bar(
    graf2,
    x="categoria",
    y="valor",
    color="valor",
    color_continuous_scale="reds"
)

st.plotly_chart(fig2, use_container_width=True)

# ------------------------------------------------
# EVOLUÇÃO FINANCEIRA
# ------------------------------------------------

st.subheader("Evolução financeira")

graf3 = df.groupby(["mes", "tipo"])["valor"].sum().reset_index()

fig3 = px.line(
    graf3,
    x="mes",
    y="valor",
    color="tipo",
    markers=True
)

st.plotly_chart(fig3, use_container_width=True)

# ------------------------------------------------
# RECEITA X DESPESA
# ------------------------------------------------

st.subheader("Receita x Despesa")

rd = df[df["tipo"].isin(["receita", "despesa"])]

graf4 = rd.groupby(["mes", "tipo"])["valor"].sum().reset_index()

fig4 = px.bar(
    graf4,
    x="mes",
    y="valor",
    color="tipo",
    barmode="group"
)

st.plotly_chart(fig4, use_container_width=True)