"""Carregamento dos dados processados pelo pipeline (pasta data/processed)."""

from pathlib import Path

import pandas as pd
import streamlit as st

PASTA = Path(__file__).resolve().parent.parent / "data" / "processed"


@st.cache_data
def carregar(nome: str) -> pd.DataFrame | None:
    """Lê data/processed/<nome>.csv; devolve None se o arquivo ainda não existir."""
    caminho = PASTA / f"{nome}.csv"
    if not caminho.exists():
        return None
    return pd.read_csv(caminho)
