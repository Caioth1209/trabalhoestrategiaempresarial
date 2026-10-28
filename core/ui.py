"""Componentes visuais compartilhados entre as páginas."""

import streamlit as st

from core.fontes import FONTES
from core.glossario import SIGLAS

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


def sem_latex(texto: str) -> str:
    """Escapa "$" para o Streamlit não ler "R$ ... R$" como fórmula matemática."""
    return texto.replace("$", "\\$")


def legenda(*siglas: str) -> None:
    """Caixa expansível que explica as siglas usadas na página."""
    with st.expander("📖 Legenda das siglas"):
        st.markdown("\n".join(f"- **{s}**: {sem_latex(SIGLAS[s])}" for s in sorted(siglas, key=str.lower)))


def dados_pendentes(descricao: str) -> None:
    st.info(f"Dados em coleta. Esta seção vai mostrar: {descricao}", icon="⏳")


def barra_lateral() -> None:
    with st.sidebar:
        st.markdown(
            f"**Rivalidade no setor de Agências de Viagem (CNAE 79)**\n\n"
            f"{AUTOR}  \n{DISCIPLINA} · {PROFESSOR}  \n{INSTITUICAO} · AP1"
        )
