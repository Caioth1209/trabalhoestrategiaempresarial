"""Componentes visuais compartilhados entre as páginas."""

import streamlit as st

from core.fontes import FONTES

AUTOR = "Caio Araujo da Luz"
DISCIPLINA = "Estratégia Empresarial"
PROFESSOR = "Prof. Paulo Tostes"
INSTITUICAO = "Ibmec"


def cabecalho(titulo: str, subtitulo: str = "") -> None:
    st.title(titulo)
    if subtitulo:
        st.caption(subtitulo)


def citar(*chaves: str) -> None:
    """Rodapé com as fontes usadas na página."""
    itens = " · ".join(f"[{FONTES[c]['nome']}]({FONTES[c]['url']})" for c in chaves)
    st.caption(f"**Fontes:** {itens}")


def dados_pendentes(descricao: str) -> None:
    st.info(f"Dados em coleta. Esta seção vai mostrar: {descricao}", icon="⏳")


def barra_lateral() -> None:
    with st.sidebar:
        st.markdown(
            f"**Rivalidade no setor de Agências de Viagem (CNAE 79)**\n\n"
            f"{AUTOR}  \n{DISCIPLINA} · {PROFESSOR}  \n{INSTITUICAO} · AP1"
        )
