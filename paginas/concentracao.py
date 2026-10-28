import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from core.dados import cempre79, cnpj79, cvc
from core.graficos import CORES, marcar_eventos, num, pct
from core.ui import cabecalho, citar

cabecalho("Estrutura e concentração", "O mercado é dominado por poucas empresas ou pulverizado?")

df = cvc().dropna(subset=["participacao"])
pico = df.loc[df["participacao"].idxmax()]
ult = df.iloc[-1]

c1, c2, c3 = st.columns(3)
c1.metric(f"Participação da CVC ({int(ult.ano)})", pct(ult.participacao),
          f"{(ult.participacao - pico.participacao) * 100:+.1f}".replace(".", ",") + " p.p. desde o pico",
          delta_color="off")
c2.metric(f"Pico da série ({int(pico.ano)})", pct(pico.participacao))
c3.metric("HHI mínimo compatível", num(ult.participacao ** 2 * 10_000),
          help="O HHI é a soma dos quadrados das participações (0 a 10.000). Só a CVC já contribui com "
               "este valor; o restante do mercado é formado por milhares de empresas pequenas, "
               "o que mantém o índice muito abaixo de 1.500, o limite de mercado 'não concentrado'.")

st.subheader("Participação da líder na receita do setor (CR1)")
fig = go.Figure()
fig.add_bar(x=df.ano, y=df.participacao, marker_color=CORES[0], hovertemplate="%{y:.1%}",
            name="CVC / setor")
fig.update_layout(yaxis_tickformat=".0%", height=360, showlegend=False,
                  yaxis_title="Receita CVC ÷ receita CNAE 79")
st.plotly_chart(marcar_eventos(fig, anual=True), use_container_width=True)
st.caption("Receita líquida consolidada da CVC (CVM) dividida pela receita operacional líquida da CNAE 79 (PAS). "
           "A receita consolidada da CVC inclui as operações na Argentina adquiridas a partir de 2018, "
           "então a participação no Brasil pode estar levemente superestimada nesses anos.")
st.markdown(
    f"Mesmo a maior empresa do país responde por menos de um sexto da receita, e a fatia dela caiu de "
    f"**{pct(pico.participacao)}** em {int(pico.ano)} para **{pct(ult.participacao)}** em {int(ult.ano)}. "
    "Isso indica um mercado **fragmentado e cada vez mais disputado**, com espaço tomado por agências "
    "online e pequenos operadores."
)

st.subheader("Tamanho típico das empresas")
cem = cempre79()
cem = cem[cem["codigo"] != "79"]
c1, c2 = st.columns(2)
fig = px.line(cem, x="ano", y="pessoas_por_empresa", color="nome", markers=True,
              color_discrete_sequence=CORES, labels={"pessoas_por_empresa": "Pessoas por empresa", "nome": ""})
fig.update_traces(hovertemplate="%{y:.1f}")
fig.add_vrect(x0=2021.5, x1=2024.5, fillcolor="#eceae4", opacity=0.5, line_width=0)
fig.update_layout(height=380, title="Pessoal ocupado médio por empresa")
c1.plotly_chart(fig, use_container_width=True)
ultimo = cem[cem["ano"] == cem["ano"].max()]
fig = px.bar(ultimo, x="empresas", y="nome", orientation="h", color="nome",
             color_discrete_sequence=CORES, labels={"empresas": "Empresas", "nome": ""})
fig.update_layout(height=380, showlegend=False, title=f"Empresas por subclasse ({int(ultimo.ano.max())})")
c2.plotly_chart(fig, use_container_width=True)
st.caption("CEMPRE/IBGE. A área cinza marca a nova série do CEMPRE (2022 em diante), que passou a incluir "
           "mais empresas pequenas, por isso a média cai em degrau.")

base = cnpj79()
if base is not None and "porte_nome" in base:
    st.subheader("Porte das empresas ativas")
    ativas = base[base["ativa"]]
    c1, c2 = st.columns(2)
    porte = ativas["porte_nome"].value_counts().reset_index()
    fig = px.bar(porte, x="count", y="porte_nome", orientation="h", color_discrete_sequence=[CORES[0]],
                 labels={"count": "Empresas ativas", "porte_nome": ""})
    fig.update_layout(height=300)
    c1.plotly_chart(fig, use_container_width=True)
    if "mei" in ativas:
        c2.metric("Empresas ativas (Receita Federal)", num(len(ativas)))
        c2.metric("São MEI", pct(ativas["mei"].mean()))
        c2.metric("Micro ou pequeno porte", pct(ativas["porte"].isin(["01", "03"]).mean()))
    st.caption("Porte declarado no CNPJ (Receita Federal). ME = receita até R$ 360 mil/ano; "
               "EPP = até R$ 4,8 mi/ano.")

    st.subheader("Onde estão as empresas")
    uf = ativas["uf"].value_counts().reset_index()
    uf["participacao"] = uf["count"] / uf["count"].sum()
    fig = px.bar(uf, x="uf", y="count", color_discrete_sequence=[CORES[0]],
                 labels={"count": "Empresas ativas", "uf": ""}, custom_data=["participacao"])
    fig.update_traces(hovertemplate="%{x}: %{y:,} (%{customdata[0]:.1%})")
    fig.update_layout(height=340)
    st.plotly_chart(fig, use_container_width=True)
    top3 = uf.head(3)
    st.caption(f"{', '.join(top3.uf)} concentram {pct(top3.participacao.sum())} das empresas ativas.")

citar("cvm", "pas", "cempre", "cnpj")
