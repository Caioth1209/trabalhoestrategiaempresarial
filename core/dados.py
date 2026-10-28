"""Carregamento dos dados processados (data/processed) e indicadores derivados."""

from pathlib import Path

import pandas as pd
import streamlit as st

PASTA = Path(__file__).resolve().parent.parent / "data" / "processed"
AGENCIAS_PAS = "Agências de viagens, operadores turísticos e outros serviços de turismo"


@st.cache_data
def _ler(caminho: Path, modificado: float) -> pd.DataFrame:
    # "modificado" entra na chave do cache: se o arquivo for atualizado, relê
    return pd.read_parquet(caminho) if caminho.suffix == ".parquet" else pd.read_csv(caminho)


def carregar(nome: str) -> pd.DataFrame | None:
    """Lê data/processed/<nome>.parquet ou .csv; devolve None se ainda não existir."""
    for ext in (".parquet", ".csv"):
        caminho = PASTA / f"{nome}{ext}"
        if caminho.exists():
            return _ler(caminho, caminho.stat().st_mtime)
    return None


@st.cache_data
def ipca_anual() -> pd.Series:
    """Fator para levar valores de cada ano a preços do último ano completo (média anual do IPCA)."""
    ipca = carregar("ipca")
    ipca["ano"] = pd.to_datetime(ipca["data"]).dt.year
    media = ipca.groupby("ano")["ipca_indice"].agg(["mean", "size"])
    media = media[media["size"] == 12]["mean"]
    return media.iloc[-1] / media


@st.cache_data
def pas() -> pd.DataFrame:
    df = carregar("pas_atividades").copy()
    fator = ipca_anual()
    df["receita_real"] = df["receita_liquida"] * df["ano"].map(fator)
    df["receita_por_empresa"] = df["receita_liquida"] / df["empresas"]
    df["pessoas_por_empresa"] = df["pessoal_ocupado"] / df["empresas"]
    df["va_sobre_receita"] = df["valor_adicionado"] / df["receita_liquida"]
    df["salario_medio_anual"] = df["salarios"] / df["pessoal_ocupado"]
    df["setor_79"] = df["atividade"] == AGENCIAS_PAS
    return df


@st.cache_data
def pas_agencias() -> pd.DataFrame:
    df = pas()
    return df[df["setor_79"]].sort_values("ano").reset_index(drop=True)


@st.cache_data
def cvc() -> pd.DataFrame:
    """DRE da CVC + participação na receita do setor (PAS)."""
    df = carregar("cvm_cvc").copy()
    setor = pas_agencias().set_index("ano")["receita_liquida"]
    df["receita_setor"] = df["ano"].map(setor)
    df["participacao"] = df["receita_liquida"] / df["receita_setor"]
    return df


@st.cache_data
def cempre79() -> pd.DataFrame:
    df = carregar("cempre_divisoes")
    df = df[df["codigo"].astype(str).str.startswith("79")].copy()
    df["pessoas_por_empresa"] = df["pessoal_ocupado"] / df["empresas"]
    return df


@st.cache_data
def pms_turismo() -> pd.DataFrame:
    df = carregar("pms_turismo").copy()
    df["data"] = pd.to_datetime(df["data"])
    largo = df.pivot_table(index=["data", "ajuste"], columns="serie", values="indice").reset_index()
    largo.columns.name = None
    # receita nominal / volume = índice de preço implícito dos serviços turísticos
    largo["preco_implicito"] = largo["receita nominal"] / largo["volume"] * 100
    return largo


SUBCLASSES = {"7911200": "Agências de viagens", "7912100": "Operadores turísticos",
              "7990200": "Reservas e outros serviços"}
PORTES = {"01": "Microempresa", "03": "Pequeno porte (EPP)", "05": "Demais", "00": "Não informado"}


@st.cache_data
def cnpj79() -> pd.DataFrame | None:
    """Uma linha por empresa (matriz) da CNAE 79, com porte, MEI, abertura e baixa."""
    estab = carregar("cnpj_estab_79")
    if estab is None:
        return None
    df = estab[estab["matriz_filial"] == "1"].copy()
    df["abertura"] = pd.to_datetime(df["data_inicio"], format="%Y%m%d", errors="coerce")
    df["data_sit"] = pd.to_datetime(df["data_situacao"], format="%Y%m%d", errors="coerce")
    df["ativa"] = df["situacao"] == "02"
    df["baixa"] = df["data_sit"].where(df["situacao"] == "08")
    df["subclasse"] = df["cnae"].map(SUBCLASSES)
    emp = carregar("cnpj_empresas_79")
    if emp is not None:
        emp = emp.drop_duplicates("cnpj_basico")
        df = df.merge(emp[["cnpj_basico", "razao_social", "porte", "capital_social"]], on="cnpj_basico", how="left")
        df["porte_nome"] = df["porte"].map(PORTES).fillna("Não informado")
    simples = carregar("cnpj_simples_79")
    if simples is not None:
        simples = simples.drop_duplicates("cnpj_basico")
        df = df.merge(simples[["cnpj_basico", "opcao_mei", "opcao_simples"]], on="cnpj_basico", how="left")
        df["mei"] = df["opcao_mei"] == "S"
    return df


@st.cache_data
def entrada_saida() -> pd.DataFrame | None:
    """Aberturas, baixas, estoque ativo e taxas por ano (empresas matriz da CNAE 79)."""
    df = cnpj79()
    if df is None:
        return None
    ab = df.groupby(df["abertura"].dt.year).size().rename("aberturas")
    bx = df.groupby(df["baixa"].dt.year).size().rename("baixas")
    out = pd.concat([ab, bx], axis=1).fillna(0).astype(int)
    out.index = out.index.astype(int)
    out = out.loc[1995:].reset_index(names="ano")
    # estoque reconstruído: empresas abertas até o ano e ainda não baixadas
    out["estoque"] = (out["aberturas"].cumsum() - out["baixas"].cumsum()
                      + len(df[(df["abertura"].dt.year < 1995) & ~(df["baixa"].dt.year < 1995)]))
    out["taxa_entrada"] = out["aberturas"] / out["estoque"].shift()
    out["taxa_saida"] = out["baixas"] / out["estoque"].shift()
    out["entrada_liquida"] = out["aberturas"] - out["baixas"]
    return out
