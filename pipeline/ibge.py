"""Coleta de séries do IBGE via API SIDRA.

Gera em data/processed:
- pms_turismo.csv : índice mensal das atividades turísticas (tabela 8694)
- pms_atividades.csv : índice de volume da PMS por atividade de serviço (tabela 8688)
- cempre_divisoes.csv : empresas, pessoal e salários por divisão/classe CNAE,
  2006-2024 (tabelas 6449 e 9418)

Uso: python -m pipeline.ibge
"""

import re
import time
from pathlib import Path

import pandas as pd
import requests

OUT = Path(__file__).resolve().parent.parent / "data" / "processed"
API = "https://apisidra.ibge.gov.br/values"


def sidra(caminho: str) -> pd.DataFrame:
    for tentativa in range(5):
        try:
            r = requests.get(f"{API}{caminho}", timeout=180)
            r.raise_for_status()
            dados = r.json()
            break
        except (requests.RequestException, ValueError):
            time.sleep(2 ** tentativa)
    else:
        raise RuntimeError(f"falha ao consultar {caminho}")
    cab = dados[0]
    df = pd.DataFrame(dados[1:]).rename(columns=cab)
    df["Valor"] = pd.to_numeric(df["Valor"], errors="coerce")
    return df


def pms_turismo() -> pd.DataFrame:
    # 7167 = número-índice, 7168 = número-índice com ajuste sazonal
    df = sidra("/t/8694/n1/all/v/7167,7168/p/all/c11046/all")
    df["data"] = pd.to_datetime(df["Mês (Código)"], format="%Y%m")
    df["serie"] = df["Tipos de índice"].str.replace("Índice de ", "").str.replace(" das atividades turísticas", "")
    df["ajuste"] = df["Variável"].str.contains("sazonal").map({True: "com ajuste", False: "sem ajuste"})
    return df[["data", "serie", "ajuste", "Valor"]].rename(columns={"Valor": "indice"})


def pms_atividades() -> pd.DataFrame:
    df = sidra("/t/8688/n1/all/v/7167/p/all/c11046/all/c12355/all")
    df = df[df["Tipos de índice"].str.contains("volume")]
    df["data"] = pd.to_datetime(df["Mês (Código)"], format="%Y%m")
    return df[["data", "Atividades de serviços", "Valor"]].rename(
        columns={"Atividades de serviços": "atividade", "Valor": "indice_volume"})


def ipca() -> pd.DataFrame:
    """IPCA número-índice mensal (tabela 1737), para deflacionar valores."""
    df = sidra("/t/1737/n1/all/v/2266/p/all")
    df["data"] = pd.to_datetime(df["Mês (Código)"], format="%Y%m")
    return df[["data", "Valor"]].rename(columns={"Valor": "ipca_indice"}).query("data >= '2005-01-01'")


def cempre() -> pd.DataFrame:
    partes = []
    for tabela, periodos in [(6449, range(2006, 2022)), (9418, range(2022, 2025))]:
        for ano in periodos:
            df = sidra(f"/t/{tabela}/n1/all/v/allxp/p/{ano}/c12762/all")
            cnae = df["Classificação Nacional de Atividades Econômicas (CNAE 2.0)"]
            # mantém divisões (2 dígitos) e as classes da divisão 79
            df = df[cnae.str.match(r"^\d{2} ") | cnae.str.match(r"^79\.\d{2}-\d ")]
            df = df.assign(ano=ano, cnae=df["Classificação Nacional de Atividades Econômicas (CNAE 2.0)"])
            partes.append(df[["ano", "cnae", "Variável", "Valor"]])
            print(f"CEMPRE {ano}: {len(df)} linhas", flush=True)
    longo = pd.concat(partes)
    largo = longo.pivot_table(index=["ano", "cnae"], columns="Variável", values="Valor").reset_index()
    largo.columns.name = None
    largo = largo.rename(columns={
        "Número de empresas e outras organizações": "empresas",
        "Pessoal ocupado total": "pessoal_ocupado",
        "Pessoal ocupado assalariado": "pessoal_assalariado",
        "Salários e outras remunerações": "salarios_mil",
    })
    largo["codigo"] = largo["cnae"].str.extract(r"^([\d.\-]+)")
    largo["nome"] = largo["cnae"].str.replace(r"^[\d.\-]+ ", "", regex=True)
    return largo[["ano", "codigo", "nome", "empresas", "pessoal_ocupado", "pessoal_assalariado", "salarios_mil"]]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    pms_turismo().to_csv(OUT / "pms_turismo.csv", index=False)
    print("PMS turismo ok", flush=True)
    pms_atividades().to_csv(OUT / "pms_atividades.csv", index=False)
    print("PMS atividades ok", flush=True)
    ipca().to_csv(OUT / "ipca.csv", index=False)
    print("IPCA ok", flush=True)
    cempre().to_csv(OUT / "cempre_divisoes.csv", index=False)
    print("CEMPRE ok", flush=True)


if __name__ == "__main__":
    main()
