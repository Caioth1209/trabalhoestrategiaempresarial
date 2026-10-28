import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from core.dados import carregar, pas
from core.graficos import CONTEXTO, DESTAQUE, pct
from core.ui import cabecalho, citar, legenda

cabecalho("Comparativo setorial", "Como as agências de viagem se comparam com outros serviços")

# Atividades "folha" da PAS (exclui totais e agregados) para comparar setores do mesmo nível
AGREGADOS = {
    "Total", "Serviços prestados principalmente às famílias", "Serviços de informação e comunicação",
    "Serviços profissionais, administrativos e complementares",
    "Transportes, serviços auxiliares aos transportes e correio",
    "Transporte e serviços auxiliares aos transportes", "Transporte rodoviário", "Atividades imobiliárias",
    "Serviços de manutenção e reparação", "Outras atividades de serviços",
}
df = pas()
df = df[~df["atividade"].isin(AGREGADOS)]
anos = sorted(df["ano"].unique())

c1, c2 = st.columns(2)
ano_ini = c1.selectbox("Ano inicial", anos, index=anos.index(2019))
ano_fim = c2.selectbox("Ano final", anos, index=len(anos) - 1)

ini = df[df.ano == ano_ini].set_index("atividade")
fim = df[df.ano == ano_fim].set_index("atividade")
comp = pd.DataFrame({
    "crescimento_real": fim["receita_real"] / ini["receita_real"] - 1,
    "va_sobre_receita": fim["va_sobre_receita"],
    "pessoas_por_empresa": fim["pessoas_por_empresa"],
    "receita_por_empresa": fim["receita_por_empresa"] / 1e3,
}).dropna().reset_index()
comp["destaque"] = comp["atividade"].str.startswith("Agências de viagens")


def ranking(coluna: str, titulo: str, formato: str):
    d = comp.sort_values(coluna)
    fig = go.Figure(go.Bar(
        x=d[coluna], y=d["atividade"], orientation="h",
        marker_color=[DESTAQUE if x else CONTEXTO for x in d["destaque"]],
        hovertemplate="%{y}: %{x:" + formato + "}<extra></extra>",
    ))
    fig.update_layout(title=titulo, height=720, xaxis_tickformat=formato, yaxis_tickfont_size=11,
                      hovermode="closest")
    st.plotly_chart(fig, use_container_width=True)
    pos = d["atividade"].tolist()[::-1].index(d[d["destaque"]]["atividade"].iloc[0]) + 1
    return pos, len(d)


tab1, tab2, tab3 = st.tabs(["Crescimento real", "Valor adicionado / receita", "Tamanho médio"])
with tab1:
    pos, n = ranking("crescimento_real", f"Crescimento real da receita, {ano_ini}–{ano_fim}", ".0%")
    st.caption(f"Agências de viagens ficam em {pos}º de {n} atividades. Receita deflacionada pelo IPCA.")
with tab2:
    pos, n = ranking("va_sobre_receita", f"Valor adicionado / receita, {ano_fim}", ".0%")
    st.caption(f"Agências de viagens ficam em {pos}º de {n}. Quanto menor, menos valor fica com a empresa "
               "a cada real vendido.")
with tab3:
    pos, n = ranking("pessoas_por_empresa", f"Pessoal ocupado por empresa, {ano_fim}", ".1f")
    st.caption(f"Agências de viagens ficam em {pos}º de {n}. Empresas pequenas e numerosas são sinal de "
               "barreiras de entrada baixas.")

div = carregar("cnpj_divisoes")
if div is not None:
    st.subheader("Entrada de novas empresas: CNAE 79 versus todas as divisões")
    ult = div[div["ano"].between(2019, 2025)].groupby("divisao")[["aberturas", "encerramentos"]].sum()
    ult = ult.join(div.groupby("divisao")["ativas_hoje"].first())
    ult = ult[ult["ativas_hoje"] >= 1000]
    ult["taxa_entrada_anual"] = ult["aberturas"] / 7 / ult["ativas_hoje"]
    ult["taxa_saida_anual"] = ult["encerramentos"] / 7 / ult["ativas_hoje"]
    ult = ult.reset_index()
    ult["divisao"] = ult["divisao"].astype(str).str.zfill(2)
    ult["destaque"] = ult["divisao"] == "79"
    fig = px.scatter(ult, x="taxa_entrada_anual", y="taxa_saida_anual", hover_name="divisao",
                     color="destaque", color_discrete_map={True: DESTAQUE, False: CONTEXTO},
                     labels={"taxa_entrada_anual": "Aberturas por ano ÷ empresas ativas",
                             "taxa_saida_anual": "Baixas por ano ÷ empresas ativas"})
    fig.update_traces(marker_size=9)
    fig.update_layout(height=440, showlegend=False, xaxis_tickformat=".0%", yaxis_tickformat=".0%",
                      hovermode="closest")
    st.plotly_chart(fig, use_container_width=True)
    a79 = ult[ult["destaque"]].iloc[0]
    st.caption(f"Cada ponto é uma divisão CNAE (média 2019-2025). A CNAE 79, em azul, tem taxa de entrada de "
               f"{pct(a79.taxa_entrada_anual)} ao ano, contra mediana de {pct(ult.taxa_entrada_anual.median())} "
               "entre as divisões.")

citar("pas", "ipca", "cnpj")
legenda('PAS', 'IPCA', 'CNAE', 'CNPJ')
