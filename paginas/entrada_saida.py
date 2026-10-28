import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from core.dados import cnpj79, entrada_saida
from core.graficos import CORES, marcar_eventos, num, pct
from core.ui import cabecalho, citar, dados_pendentes

cabecalho("Entrada e saída de concorrentes", "Barreiras de entrada e dinâmica competitiva")

es = entrada_saida()
if es is None:
    dados_pendentes("aberturas e encerramentos de agências por ano, taxa líquida de entrada e sobrevivência.")
    st.stop()

base = cnpj79()
es = es[es["ano"].between(2000, 2025)]
ult = es[es["ano"] == 2025].iloc[0]
media_10 = es[es["ano"].between(2016, 2025)]

c1, c2, c3, c4 = st.columns(4)
c1.metric("Empresas ativas hoje", num(base["ativa"].sum()))
c2.metric("Aberturas em 2025", num(ult.aberturas))
c3.metric("Baixas em 2025", num(ult.baixas))
c4.metric("Taxa de entrada média (2016-25)", pct(media_10["taxa_entrada"].mean()),
          help="Aberturas no ano ÷ estoque de empresas no fim do ano anterior.")

st.subheader("Aberturas e baixas por ano")
fig = go.Figure()
fig.add_bar(x=es.ano, y=es.aberturas, name="Aberturas", marker_color=CORES[0])
fig.add_bar(x=es.ano, y=-es.baixas, name="Baixas", marker_color=CORES[1],
            customdata=es.baixas, hovertemplate="%{customdata:,}")
fig.add_scatter(x=es.ano, y=es.entrada_liquida, name="Entrada líquida", mode="lines+markers",
                line_color="#14213D")
fig.update_layout(barmode="relative", height=420, yaxis_title="Empresas (matriz)")
st.plotly_chart(marcar_eventos(fig, anual=True), use_container_width=True)
st.caption("Empresas (matriz) com CNAE principal 79 no cadastro atual da Receita Federal. "
           "Baixas consideram a data da situação 'baixada'.")

st.subheader("Taxas de entrada e de saída")
fig = go.Figure()
fig.add_scatter(x=es.ano, y=es.taxa_entrada, name="Taxa de entrada", line_color=CORES[0])
fig.add_scatter(x=es.ano, y=es.taxa_saida, name="Taxa de saída", line_color=CORES[1])
fig.update_layout(yaxis_tickformat=".0%", height=360)
st.plotly_chart(marcar_eventos(fig, anual=True), use_container_width=True)

st.subheader("Sobrevivência das novas empresas")
coortes = base[base["abertura"].dt.year.between(2010, 2022)].copy()
coortes["coorte"] = coortes["abertura"].dt.year
vida = (coortes["baixa"].fillna(pd.Timestamp("2026-10-01")) - coortes["abertura"]).dt.days / 365.25
linhas = []
for anos in (1, 3, 5):
    vivas = coortes.assign(viva=(vida >= anos) | coortes["baixa"].isna())
    ok = vivas[vivas["coorte"] <= 2025 - anos]
    taxa = ok.groupby("coorte")["viva"].mean().rename("sobrevivencia").reset_index()
    taxa["horizonte"] = f"{anos} ano{'s' if anos > 1 else ''}"
    linhas.append(taxa)
sob = pd.concat(linhas)
fig = px.line(sob, x="coorte", y="sobrevivencia", color="horizonte", markers=True,
              color_discrete_sequence=CORES, labels={"coorte": "Ano de abertura", "sobrevivencia": ""})
fig.update_layout(yaxis_tickformat=".0%", height=360, legend_title_text="Sobrevive após")
st.plotly_chart(fig, use_container_width=True)
st.caption("Proporção das empresas abertas em cada ano que não tinham sido baixadas depois de 1, 3 e 5 anos. "
           "Empresas inaptas ou suspensas contam como sobreviventes, então a sobrevivência real é menor.")

st.subheader("Quem está entrando")
c1, c2 = st.columns(2)
rec = base[base["abertura"].dt.year >= 2022]
sub = rec["subclasse"].value_counts().reset_index()
fig = px.bar(sub, x="count", y="subclasse", orientation="h", color_discrete_sequence=[CORES[0]],
             labels={"count": "Aberturas desde 2022", "subclasse": ""})
fig.update_layout(height=280)
c1.plotly_chart(fig, use_container_width=True)
if "mei" in rec:
    c2.metric("Novas empresas (2022 em diante) que são MEI", pct(rec["mei"].mean()))
    c2.metric("Microempresas entre as novas", pct((rec["porte"] == "01").mean()))
    c2.caption("Entrantes pequenos indicam barreiras de entrada baixas: basta um CNPJ, um computador "
               "e acesso aos sistemas de reserva.")

citar("cnpj")
