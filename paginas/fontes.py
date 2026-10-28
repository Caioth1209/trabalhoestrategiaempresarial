import streamlit as st

from core.fontes import FONTES
from core.ui import cabecalho

cabecalho("Fontes e metodologia", "De onde vêm os dados e como foram tratados")

for f in FONTES.values():
    with st.container(border=True):
        st.markdown(f"**[{f['nome']}]({f['url']})**  \n{f['uso']}")

st.subheader("Limitações")
st.markdown(
    "- Não há dado público de *market share* por empresa para todo o setor. "
    "A concentração é estimada pela receita das empresas listadas dividida pela receita total da CNAE 79 na PAS.\n"
    "- A PAS é anual e é divulgada com cerca de dois anos de defasagem."
)
