import plotly.graph_objects as go
import streamlit as st

from core.dados import cempre79, ipca_anual, pas_agencias, pms_turismo
from core.graficos import CORES, brl, marcar_eventos, num, pct
from core.ui import cabecalho, citar

cabecalho("Visão geral do setor", "Agências de viagens, operadores turísticos e serviços de reservas (CNAE 79)")

pas = pas_agencias()
ult, ant = pas.iloc[-1], pas.iloc[-2]
cem = cempre79()
cem79 = cem[cem["codigo"] == "79"].sort_values("ano")

st.markdown(
    "O setor reúne **agências de viagens** (CNAE 7911-2), **operadoras turísticas** (7912-1) e "
    "**serviços de reservas** (7990-2). Ele intermedeia a venda de passagens, hospedagem e pacotes, "
    "e vem passando por uma transformação: a migração da venda para canais online (OTAs), "
    "o choque da pandemia e a quebra de agências que vendiam passagens a prazo para entrega futura."
)

c1, c2, c3, c4 = st.columns(4)
c1.metric(f"Receita líquida ({int(ult.ano)})", brl(ult.receita_liquida),
          pct(ult.receita_liquida / ant.receita_liquida - 1) + " vs ano anterior")
c2.metric(f"Empresas – PAS ({int(ult.ano)})", num(ult.empresas),
          pct(ult.empresas / ant.empresas - 1))
c3.metric(f"Pessoal ocupado ({int(ult.ano)})", num(ult.pessoal_ocupado),
          pct(ult.pessoal_ocupado / ant.pessoal_ocupado - 1))
c4.metric(f"Empresas – CEMPRE ({int(cem79.ano.iloc[-1])})", num(cem79.empresas.iloc[-1]),
          help="O CEMPRE conta todas as empresas formais; a PAS considera só as que têm receita de serviços no ano.")

st.subheader("Receita do setor: nominal e real")
fig = go.Figure()
fig.add_scatter(x=pas.ano, y=pas.receita_liquida / 1e6, name="Nominal", line_color=CORES[0],
                hovertemplate="R$ %{y:.1f} bi")
fig.add_scatter(x=pas.ano, y=pas.receita_real / 1e6, name=f"Real (preços de {ipca_anual().index[-1]})",
                line_color=CORES[1], hovertemplate="R$ %{y:.1f} bi")
fig.update_layout(yaxis_title="R$ bilhões", height=380)
st.plotly_chart(marcar_eventos(fig, anual=True), use_container_width=True)
st.caption("Receita operacional líquida da PAS. Valores reais corrigidos pela média anual do IPCA.")

st.subheader("Demanda por turismo, mês a mês")
pms = pms_turismo()
pms = pms[pms["ajuste"] == "com ajuste"]
fig = go.Figure()
fig.add_scatter(x=pms.data, y=pms.volume, name="Volume", line_color=CORES[0], hovertemplate="%{y:.1f}")
fig.add_scatter(x=pms.data, y=pms["receita nominal"], name="Receita nominal", line_color=CORES[1],
                hovertemplate="%{y:.1f}")
fig.update_layout(yaxis_title="Índice (2022 = 100)", height=380)
st.plotly_chart(marcar_eventos(fig), use_container_width=True)
st.caption("Índice de atividades turísticas da PMS, com ajuste sazonal. "
           "A distância entre receita e volume indica aumento de preços.")

st.subheader("Linha do tempo")
st.markdown("""
| Ano | Evento | Efeito na rivalidade |
|---|---|---|
| 2013 | CVC abre capital na B3 | Líder ganha fôlego para expandir lojas e adquirir rivais |
| 2015-16 | Recessão | Receita real cai; competição por preço |
| 2018 | Pico de participação da CVC (≈15% da receita do setor) | Concentração máxima da série |
| 2020 | Pandemia | Receita cai à metade; cerca de 2,8 mil empresas deixam a PAS |
| 2022-23 | Retomada; 123milhas e Hurb entram em crise (2023) | Muitos novos entrantes; desconfiança do consumidor com vendas antecipadas |
""")

citar("pas", "pms", "cempre", "ipca")
