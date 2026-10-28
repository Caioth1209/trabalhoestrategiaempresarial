import pandas as pd
import plotly.express as px
import streamlit as st

from core.dados import cempre79, cvc, entrada_saida, pas, pas_agencias, pms_turismo
from core.graficos import CORES, marcar_eventos
from core.ui import cabecalho, citar

cabecalho("Explorador de dados", "Monte o seu painel e explore as bases livremente")

qp = st.query_params


def lista_param(nome: str) -> list[str]:
    valor = qp.get(nome, "")
    return [v for v in valor.split("|") if v]


# ---------------------------------------------------------------- painel personalizado
INDICADORES = {
    "Receita do setor (R$ bi, real)": lambda: (pas_agencias(), "ano", pas_agencias()["receita_real"] / 1e6, True),
    "Empresas (PAS)": lambda: (pas_agencias(), "ano", pas_agencias()["empresas"], True),
    "Valor adicionado / receita": lambda: (pas_agencias(), "ano", pas_agencias()["va_sobre_receita"], True),
    "Participação da CVC": lambda: (cvc(), "ano", cvc()["participacao"], True),
    "Margem EBIT da CVC": lambda: (cvc(), "ano", cvc()["margem_ebit"].clip(lower=-0.6), True),
    "Volume do turismo (PMS)": lambda: (_pms(), "data", _pms()["volume"], False),
    "Preço implícito do turismo (PMS)": lambda: (_pms(), "data", _pms()["preco_implicito"], False),
    "Pessoas por empresa (CEMPRE)": lambda: (_cem(), "ano", _cem()["pessoas_por_empresa"], True),
}
if entrada_saida() is not None:
    INDICADORES["Aberturas de empresas (CNPJ)"] = lambda: (_es(), "ano", _es()["aberturas"], True)
    INDICADORES["Entrada líquida (CNPJ)"] = lambda: (_es(), "ano", _es()["entrada_liquida"], True)


def _pms():
    d = pms_turismo()
    return d[d["ajuste"] == "com ajuste"]


def _cem():
    d = cempre79()
    return d[d["codigo"] == "79"]


def _es():
    d = entrada_saida()
    return d[d["ano"].between(2000, 2025)]


st.subheader("Meu painel")
padrao = lista_param("painel") or ["Receita do setor (R$ bi, real)", "Participação da CVC",
                                    "Valor adicionado / receita", "Volume do turismo (PMS)"]
escolhidos = st.multiselect("Indicadores", list(INDICADORES), default=[p for p in padrao if p in INDICADORES],
                            max_selections=6)
qp["painel"] = "|".join(escolhidos)

cols = st.columns(2)
for i, nome in enumerate(escolhidos):
    df, x, y, anual = INDICADORES[nome]()
    fig = px.line(x=df[x], y=y, markers=anual, color_discrete_sequence=[CORES[i % len(CORES)]])
    formato = ".0%" if any(k in nome for k in ("/", "Participação", "Margem")) else ",.1f"
    fig.update_traces(hovertemplate="%{y:" + formato + "}")
    fig.update_layout(title=nome, height=280, xaxis_title=None, yaxis_title=None, yaxis_tickformat=formato,
                      showlegend=False)
    cols[i % 2].plotly_chart(marcar_eventos(fig, anual=anual), use_container_width=True)

# ---------------------------------------------------------------- explorador livre
st.divider()
st.subheader("Explorador livre")

BASES = {
    "PAS – atividades de serviços": "pas",
    "CEMPRE – classes da CNAE 79": "cempre",
    "CVC – demonstrações financeiras": "cvc",
    "PMS – índices do turismo": "pms",
}
if entrada_saida() is not None:
    BASES["CNPJ – aberturas e baixas da CNAE 79"] = "cnpj"
nomes_bases = list(BASES)
base_qp = qp.get("base", "pas")
base = st.selectbox("Base de dados", nomes_bases,
                    index=list(BASES.values()).index(base_qp) if base_qp in BASES.values() else 0)
chave = BASES[base]
qp["base"] = chave

if chave == "pas":
    dados = pas().drop(columns=["setor_79", "chave"], errors="ignore")
    serie, eixo_x = "atividade", "ano"
elif chave == "cempre":
    dados = cempre79()
    serie, eixo_x = "nome", "ano"
elif chave == "cvc":
    dados = cvc()
    serie, eixo_x = None, "ano"
elif chave == "pms":
    dados = pms_turismo()
    serie, eixo_x = "ajuste", "data"
else:
    dados = entrada_saida()
    serie, eixo_x = None, "ano"

numericas = [c for c in dados.select_dtypes("number").columns if c != eixo_x]
var_qp = qp.get("var")
var = st.selectbox("Variável", numericas, index=numericas.index(var_qp) if var_qp in numericas else 0)
qp["var"] = var

filtrado = dados
if serie:
    opcoes = sorted(dados[serie].dropna().unique())
    sel_qp = [s for s in lista_param("sel") if s in opcoes]
    padrao_sel = sel_qp or [o for o in opcoes if "viage" in str(o).lower() or o == "com ajuste"][:1] or opcoes[:1]
    selecao = st.multiselect("Comparar", opcoes, default=padrao_sel, max_selections=8)
    qp["sel"] = "|".join(selecao)
    filtrado = dados[dados[serie].isin(selecao)]

if eixo_x == "ano":
    anos = sorted(filtrado["ano"].dropna().astype(int).unique())
    if len(anos) > 1:
        a0, a1 = st.select_slider("Período", options=anos, value=(anos[0], anos[-1]))
        filtrado = filtrado[filtrado["ano"].between(a0, a1)]

tipo = st.radio("Gráfico", ["Linha", "Barras"], horizontal=True)
kw = dict(x=eixo_x, y=var, color=serie, color_discrete_sequence=CORES)
fig = px.line(filtrado, markers=True, **kw) if tipo == "Linha" else px.bar(filtrado, barmode="group", **kw)
fig.update_layout(height=440, legend_title_text="")
st.plotly_chart(fig, use_container_width=True)

c1, c2 = st.columns([1, 2])
c1.download_button("Baixar dados filtrados (CSV)", filtrado.to_csv(index=False).encode("utf-8-sig"),
                   file_name=f"{chave}_{var}.csv", mime="text/csv")
c2.info("Para compartilhar esta análise, copie o endereço do navegador: ele guarda o painel, "
        "a base, a variável e as séries escolhidas.", icon="🔗")

with st.expander("Ver tabela"):
    st.dataframe(filtrado, use_container_width=True, hide_index=True)

citar("pas", "cempre", "cvm", "pms", "cnpj")
