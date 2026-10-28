import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import statsmodels.api as sm
import streamlit as st
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.seasonal import STL

from core.dados import cvc, entrada_saida, pas, pas_agencias, pms_turismo
from core.graficos import CONTEXTO, CORES, DESTAQUE, marcar_eventos
from core.ui import cabecalho, citar

cabecalho("Análise avançada", "Tendências, sazonalidade, projeções e relações entre indicadores")

tab1, tab2, tab3, tab4 = st.tabs(["Tendência e sazonalidade", "Projeção", "Correlações e regressão",
                                  "Agrupamento de setores"])

pms = pms_turismo()
serie = pms[pms["ajuste"] == "sem ajuste"].set_index("data")["volume"].asfreq("MS")

# ---------------------------------------------------------------- STL
with tab1:
    st.markdown("Decomposição **STL** do índice de volume do turismo (PMS): separa a série em "
                "tendência, sazonalidade e resíduo.")
    res = STL(serie, period=12, robust=True).fit()
    fig = go.Figure()
    fig.add_scatter(x=serie.index, y=serie, name="Observado", line_color=CONTEXTO)
    fig.add_scatter(x=serie.index, y=res.trend, name="Tendência", line_color=CORES[0])
    fig.update_layout(height=360, yaxis_title="Índice (2022 = 100)")
    st.plotly_chart(marcar_eventos(fig), use_container_width=True)
    saz = pd.Series(res.seasonal).groupby(serie.index.month).mean()
    meses = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]
    fig = go.Figure(go.Bar(x=meses, y=saz.values, marker_color=[CORES[0] if v >= 0 else CORES[1] for v in saz],
                           hovertemplate="%{x}: %{y:+.1f} pontos<extra></extra>"))
    fig.update_layout(title="Efeito sazonal médio por mês", height=300, yaxis_title="Pontos do índice",
                      hovermode="closest")
    st.plotly_chart(fig, use_container_width=True)
    st.caption(f"Mês mais forte: {meses[int(saz.idxmax()) - 1]}; mais fraco: {meses[int(saz.idxmin()) - 1]}. "
               "Uma sazonalidade marcada obriga as agências a disputar clientes nos meses de baixa.")

# ---------------------------------------------------------------- Holt-Winters
with tab2:
    st.markdown("Projeção do volume do turismo com **Holt-Winters** (tendência + sazonalidade), "
                "estimado só com dados pós-pandemia.")
    horizonte = st.slider("Meses à frente", 6, 24, 12)
    treino = serie["2022-01-01":]
    modelo = ExponentialSmoothing(treino, trend="add", seasonal="add", seasonal_periods=12,
                                  damped_trend=True).fit()
    prev = modelo.forecast(horizonte)
    erro = np.std(modelo.resid) * 1.96
    fig = go.Figure()
    fig.add_scatter(x=treino.index, y=treino, name="Observado", line_color=CORES[0])
    fig.add_scatter(x=prev.index, y=prev + erro, line=dict(width=0), showlegend=False, hoverinfo="skip")
    fig.add_scatter(x=prev.index, y=prev - erro, fill="tonexty", fillcolor="rgba(235,104,52,0.15)",
                    line=dict(width=0), name="Intervalo de 95%", hoverinfo="skip")
    fig.add_scatter(x=prev.index, y=prev, name="Projeção", line=dict(color=CORES[1], dash="dash"))
    fig.update_layout(height=400, yaxis_title="Índice (2022 = 100)")
    st.plotly_chart(fig, use_container_width=True)
    var12 = prev.iloc[-12:].mean() / treino.iloc[-12:].mean() - 1 if horizonte >= 12 else None
    if var12 is not None:
        st.caption(f"Média projetada dos próximos 12 meses: {var12:+.1%} em relação aos últimos 12 meses."
                   .replace(".", ","))

# ---------------------------------------------------------------- correlação e regressão
with tab3:
    ag = pas_agencias().set_index("ano")
    anual = pd.DataFrame({
        "Receita real": ag["receita_real"],
        "Empresas (PAS)": ag["empresas"],
        "Valor adicionado / receita": ag["va_sobre_receita"],
        "Receita por empresa": ag["receita_por_empresa"],
        "Participação CVC": cvc().set_index("ano")["participacao"],
        "Volume turismo (PMS)": serie.groupby(serie.index.year).mean(),
        "Preço implícito (PMS)": pms[pms["ajuste"] == "sem ajuste"].groupby(
            pms["data"].dt.year)["preco_implicito"].mean(),
    })
    es = entrada_saida()
    if es is not None:
        anual["Aberturas (CNPJ)"] = es.set_index("ano")["aberturas"]
        anual["Taxa de entrada (CNPJ)"] = es.set_index("ano")["taxa_entrada"]
    anual = anual.loc[2011:2023]
    anual.index.name = "ano"

    corr = anual.corr()
    fig = px.imshow(corr, text_auto=".2f", zmin=-1, zmax=1, aspect="auto",
                    color_continuous_scale=[[0, CORES[1]], [0.5, "#f1f0ec"], [1, CORES[0]]])
    fig.update_layout(height=520, title="Correlação entre indicadores anuais (2011-2023)", hovermode="closest")
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Correlação de Pearson. Com 13 anos de dados, use como pista, não como prova de causalidade.")

    st.markdown("**Regressão linear simples**")
    c1, c2 = st.columns(2)
    x = c1.selectbox("Variável explicativa (X)", anual.columns, index=1)
    y = c2.selectbox("Variável resposta (Y)", anual.columns, index=4)
    d = anual[[x, y]].dropna()
    if x != y and len(d) >= 5:
        ols = sm.OLS(d[y], sm.add_constant(d[x])).fit()
        fig = px.scatter(d.reset_index(), x=x, y=y, text="ano", color_discrete_sequence=[CORES[0]])
        fig.update_traces(textposition="top center", marker_size=10)
        xs = np.linspace(d[x].min(), d[x].max(), 50)
        fig.add_scatter(x=xs, y=ols.params.iloc[0] + ols.params.iloc[1] * xs, mode="lines",
                        line=dict(color=CORES[1], dash="dash"), name="Reta ajustada")
        fig.update_layout(height=420, showlegend=False, hovermode="closest")
        st.plotly_chart(fig, use_container_width=True)
        m1, m2, m3 = st.columns(3)
        m1.metric("Coeficiente", f"{ols.params.iloc[1]:.4g}")
        m2.metric("R²", f"{ols.rsquared:.2f}")
        m3.metric("p-valor", f"{ols.pvalues.iloc[1]:.3f}",
                  help="Abaixo de 0,05 a relação é estatisticamente significativa a 5%.")

# ---------------------------------------------------------------- k-means
with tab4:
    st.markdown("Agrupamento **k-means** das atividades de serviço da PAS por perfil competitivo. "
                "Setores no mesmo grupo têm estrutura parecida.")
    k = st.slider("Número de grupos", 2, 6, 4)
    df = pas()
    ini, fim = df[df.ano == 2019].set_index("atividade"), df[df.ano == df.ano.max()].set_index("atividade")
    feats = pd.DataFrame({
        "Crescimento real 2019-23": fim["receita_real"] / ini["receita_real"] - 1,
        "Valor adicionado / receita": fim["va_sobre_receita"],
        "Pessoas por empresa (log)": np.log(fim["pessoas_por_empresa"]),
        "Receita por empresa (log)": np.log(fim["receita_por_empresa"]),
    }).dropna()
    feats = feats[~feats.index.isin(["Total"])]
    z = ((feats - feats.mean()) / feats.std()).to_numpy()

    rng = np.random.default_rng(42)
    melhor = None
    for _ in range(20):  # várias inicializações, fica a de menor inércia
        centros = z[rng.choice(len(z), k, replace=False)]
        for _ in range(100):
            rot = np.argmin(((z[:, None] - centros) ** 2).sum(-1), axis=1)
            novos = np.array([z[rot == j].mean(0) if (rot == j).any() else centros[j] for j in range(k)])
            if np.allclose(novos, centros):
                break
            centros = novos
        inercia = ((z - centros[rot]) ** 2).sum()
        if melhor is None or inercia < melhor[0]:
            melhor = (inercia, rot)
    feats["grupo"] = [f"Grupo {g + 1}" for g in melhor[1]]
    feats = feats.reset_index()
    feats["agencias"] = feats["atividade"].str.startswith("Agências de viagens")

    fig = px.scatter(feats, x="Pessoas por empresa (log)", y="Valor adicionado / receita", color="grupo",
                     hover_name="atividade", color_discrete_sequence=CORES,
                     category_orders={"grupo": sorted(feats["grupo"].unique())})
    fig.update_traces(marker_size=10)
    alvo = feats[feats["agencias"]].iloc[0]
    fig.add_annotation(x=alvo["Pessoas por empresa (log)"], y=alvo["Valor adicionado / receita"],
                       text="Agências de viagens", showarrow=True, arrowhead=0, ax=40, ay=-40)
    fig.update_layout(height=460, yaxis_tickformat=".0%", hovermode="closest")
    st.plotly_chart(fig, use_container_width=True)
    pares = feats[(feats["grupo"] == alvo["grupo"]) & ~feats["agencias"]]["atividade"].tolist()
    st.caption(f"Agências de viagens caem no {alvo['grupo']}, junto com: {', '.join(pares) or 'nenhum outro setor'}.")

citar("pms", "pas", "cvm", "cnpj")
