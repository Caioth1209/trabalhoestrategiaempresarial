import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from core.dados import COMPONENTES, carregar, setores
from core.graficos import CONTEXTO, CORES, num, pct
from core.ui import cabecalho, citar, legenda

cabecalho("Rivalidade por setor", "Compare a pressão competitiva de qualquer setor da economia brasileira")

df = setores()
validos = df.dropna(subset=["indice_rivalidade"]).sort_values("indice_rivalidade", ascending=False)
n = len(validos)

st.markdown(
    "O **índice de pressão competitiva** resume, de 0 a 100, quatro sinais estruturais de rivalidade "
    "que existem para todos os setores: empresas pequenas e numerosas, muitas empresas entrando, "
    "muitas saindo e o número de empresas crescendo. Cada componente vira um percentil entre os "
    f"{n} setores, e o índice é a média deles. Quanto maior, mais disputado é o setor."
)

# ---------------------------------------------------------------- seleção (guardada na URL)
opcoes = validos["rotulo"].tolist()
por_codigo = dict(zip(validos["codigo"], validos["rotulo"]))
qp = st.query_params
padrao = [por_codigo[c] for c in qp.get("setores", "79|47|56").split("|") if c in por_codigo]
escolha = st.multiselect("Setores (divisão CNAE)", opcoes, default=padrao or opcoes[:1], max_selections=5)
if not escolha:
    st.info("Escolha pelo menos um setor.")
    st.stop()
sel = validos.set_index("rotulo").loc[escolha].reset_index()
qp["setores"] = "|".join(sel["codigo"])
cor = {r: CORES[i] for i, r in enumerate(escolha)}
curto = {r: r if len(r) <= 34 else r[:33] + "…" for r in escolha}
cor_curto = {curto[r]: c for r, c in cor.items()}

# ---------------------------------------------------------------- índice dos escolhidos
cols = st.columns(len(sel))
for col, (_, s) in zip(cols, sel.iterrows()):
    col.metric(f"{s.codigo} – {s.nome[:38]}{'…' if len(s.nome) > 38 else ''}", f"{s.indice_rivalidade:.0f} / 100")
    col.caption(f"{int(s.posicao)}º mais disputado de {n} setores")

st.subheader("Componentes do índice")
longo = sel.melt(id_vars=["rotulo"], value_vars=[f"pct_{c}" for c in COMPONENTES],
                 var_name="componente", value_name="percentil")
longo["componente"] = longo["componente"].str.removeprefix("pct_").map(COMPONENTES)
fig = px.bar(longo, x="percentil", y="componente", color="rotulo", barmode="group", orientation="h",
             color_discrete_map=cor, labels={"percentil": "Percentil entre os setores", "componente": ""})
fig.update_traces(hovertemplate="%{x:.0%}<extra>%{fullData.name}</extra>")
fig.update_layout(height=120 + 70 * len(sel), xaxis_tickformat=".0%", xaxis_range=[0, 1],
                  hovermode="closest", legend_title_text="")
st.plotly_chart(fig, use_container_width=True)
st.caption("100% = o setor está no topo daquele sinal de rivalidade; 50% = na mediana.")

st.subheader("Onde cada setor fica no ranking")
rank = validos.sort_values("indice_rivalidade")
fig = go.Figure(go.Bar(
    x=rank["indice_rivalidade"], y=rank["codigo"], orientation="h",
    marker_color=[cor.get(r, CONTEXTO) for r in rank["rotulo"]],
    customdata=rank[["nome", "posicao"]], hovertemplate="%{customdata[0]}<br>Índice %{x:.0f} · %{customdata[1]}º<extra></extra>",
))
fig.update_layout(height=max(500, 13 * n), yaxis=dict(type="category", tickfont_size=9),
                  xaxis_title="Índice de pressão competitiva", hovermode="closest", bargap=0.25)
st.plotly_chart(fig, use_container_width=True)
st.caption("Cada barra é uma divisão CNAE; passe o mouse para ver o nome. Os setores escolhidos aparecem coloridos.")

st.subheader("Indicadores")
tabela = pd.DataFrame({
    "Setor": sel["rotulo"],
    "Empresas (CEMPRE 2024)": sel["empresas"].map(num),
    "Pessoas por empresa": sel["pessoas_por_empresa"].map(lambda v: num(v, 1)),
    "Crescimento das empresas 2022-24": sel["crescimento_empresas"].map(pct),
    "Entrada anual (2019-25)": sel["taxa_entrada"].map(pct),
    "Saída anual (2019-25)": sel["taxa_saida"].map(pct),
    "Índice": sel["indice_rivalidade"].map(lambda v: f"{v:.0f}"),
})
st.dataframe(tabela, hide_index=True, use_container_width=True)

st.subheader("Evolução")
c1, c2 = st.columns(2)
cem = carregar("cempre_divisoes").assign(codigo=lambda d: d["codigo"].astype(str))
cem = cem[cem["codigo"].isin(sel["codigo"]) & (cem["ano"] >= 2022)].merge(sel[["codigo", "rotulo"]], on="codigo")
base = cem[cem["ano"] == 2022].set_index("codigo")["empresas"]
cem["indice"] = cem["empresas"] / cem["codigo"].map(base) * 100
cem["setor"] = cem["rotulo"].map(curto)
fig = px.line(cem, x="ano", y="indice", color="setor", markers=True, color_discrete_map=cor_curto,
              labels={"indice": "Empresas (2022 = 100)", "ano": ""})
fig.update_layout(title=dict(text="Número de empresas (CEMPRE)", y=0.98), height=400, xaxis_dtick=1,
                  margin_t=110, legend=dict(y=1.0, yanchor="bottom", font_size=11, title_text=""))
c1.plotly_chart(fig, use_container_width=True)

cnpj = carregar("cnpj_divisoes").assign(codigo=lambda d: d["divisao"].astype(str).str.zfill(2))
cnpj = cnpj[cnpj["codigo"].isin(sel["codigo"]) & cnpj["ano"].between(2010, 2025)].merge(
    sel[["codigo", "rotulo"]], on="codigo")
cnpj["taxa"] = cnpj["aberturas"] / cnpj["ativas_hoje"]
cnpj["setor"] = cnpj["rotulo"].map(curto)
fig = px.line(cnpj, x="ano", y="taxa", color="setor", color_discrete_map=cor_curto,
              labels={"taxa": "Aberturas ÷ empresas ativas hoje", "ano": ""})
fig.update_layout(title=dict(text="Abertura de empresas por ano (CNPJ)", y=0.98), height=400,
                  yaxis_tickformat=".0%", margin_t=110, legend=dict(y=1.0, yanchor="bottom", font_size=11, title_text=""))
c2.plotly_chart(fig, use_container_width=True)
st.caption("O CEMPRE é comparado só a partir de 2022, quando começou a série atual do IBGE.")

with st.expander("Como o índice é calculado"):
    st.markdown(f"""
- **Fragmentação**: pessoal ocupado por empresa no CEMPRE 2024, invertido (menos pessoas por empresa = mais fragmentado).
- **Entrada**: aberturas médias por ano entre 2019 e 2025 (CNPJ) ÷ empresas ativas hoje.
- **Saída**: baixas médias por ano entre 2019 e 2025 (CNPJ) ÷ empresas ativas hoje.
- **Crescimento**: variação do número de empresas no CEMPRE entre 2022 e 2024.

Cada componente vira um percentil entre os {n} setores com pelo menos mil empresas ativas, e o índice é a média
dos quatro × 100. Ficam de fora a administração pública e as associações, que não são mercados.

**Limitação:** é um índice de **estrutura** (quantos concorrentes, quão pequenos, quanto giram). Ele não mede
preços nem margens, que só existem para os setores de serviços (veja Desempenho e Comparativo).
""")

citar("cempre", "cnpj")
legenda("CNAE", "CEMPRE", "CNPJ")
