import plotly.graph_objects as go
import streamlit as st

from core.dados import cvc, pas_agencias, pms_turismo
from core.graficos import CORES, marcar_eventos, pct
from core.ui import cabecalho, citar, legenda

cabecalho("Desempenho e margens", "A rivalidade aparece nos preços e na rentabilidade")

pas = pas_agencias()

st.subheader("Quanto da receita vira valor adicionado")
st.markdown(
    "O **valor adicionado sobre a receita** mede quanto de cada real faturado fica na empresa para "
    "remunerar trabalho e capital. Quando a competição aperta, as comissões e as taxas caem e esse "
    "indicador encolhe."
)
fig = go.Figure()
fig.add_scatter(x=pas.ano, y=pas.va_sobre_receita, name="Valor adicionado / receita",
                line_color=CORES[0], mode="lines+markers", hovertemplate="%{y:.1%}")
fig.update_layout(yaxis_tickformat=".0%", height=340, showlegend=False,
                  yaxis_title="Valor adicionado / receita")
st.plotly_chart(marcar_eventos(fig, anual=True), use_container_width=True)
a, b = pas[pas.ano == 2019].iloc[0], pas.iloc[-1]
st.caption(f"Caiu de {pct(a.va_sobre_receita)} em 2019 para {pct(b.va_sobre_receita)} em {int(b.ano)}. "
           "Fonte: PAS.")

st.subheader("Margens da líder (CVC)")
df = cvc()
fig = go.Figure()
for col, nome, cor in [("margem_ebit", "Margem operacional (EBIT)", CORES[0]),
                       ("margem_liquida", "Margem líquida", CORES[1])]:
    fig.add_scatter(x=df.ano, y=df[col], name=nome, line_color=cor, mode="lines+markers",
                    hovertemplate="%{y:.1%}")
fig.add_hline(y=0, line=dict(color="#9a9893", width=1))
fig.update_layout(yaxis_tickformat=".0%", height=380, yaxis_range=[-0.7, 0.5])
st.plotly_chart(marcar_eventos(fig, anual=True), use_container_width=True)
st.caption("Em 2020 as margens ficam fora da escala (EBIT de -225% da receita) por causa de baixas contábeis. "
           "A CVC reconhece como receita só a comissão (receita líquida), não o valor bruto das viagens vendidas.")

st.subheader("Preços dos serviços turísticos")
pms = pms_turismo()
pms = pms[pms["ajuste"] == "sem ajuste"].copy()
pms["preco_12m"] = pms["preco_implicito"].rolling(12).mean()
fig = go.Figure()
fig.add_scatter(x=pms.data, y=pms.preco_12m, name="Preço implícito (média 12 meses)",
                line_color=CORES[0], hovertemplate="%{y:.1f}")
fig.update_layout(yaxis_title="Índice (2022 = 100)", height=340, showlegend=False)
st.plotly_chart(marcar_eventos(fig), use_container_width=True)
st.caption("Preço implícito = índice de receita nominal ÷ índice de volume das atividades turísticas (PMS). "
           "Mostra quanto o mesmo volume de serviço passou a custar.")

st.subheader("Produtividade e salários")
c1, c2 = st.columns(2)
fig = go.Figure(go.Bar(x=pas.ano, y=pas.receita_por_empresa / 1e3, marker_color=CORES[0],
                       hovertemplate="R$ %{y:.2f} mi"))
fig.update_layout(title="Receita média por empresa (R$ mi)", height=320)
c1.plotly_chart(fig, use_container_width=True)
fig = go.Figure(go.Bar(x=pas.ano, y=pas.salario_medio_anual, marker_color=CORES[0],
                       hovertemplate="R$ %{y:.1f} mil"))
fig.update_layout(title="Salário médio anual por pessoa (R$ mil)", height=320)
c2.plotly_chart(fig, use_container_width=True)

citar("pas", "cvm", "pms")
legenda('CVC', 'EBIT', 'PAS', 'PMS', 'CVM')
