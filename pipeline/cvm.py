"""Demonstrações financeiras anuais (DFP) da CVC Brasil, única empresa da CNAE 79
com capital aberto na B3.

Gera data/processed/cvm_cvc.csv com receita líquida, resultado bruto, resultado
operacional (EBIT) e lucro líquido consolidados, em R$ mil.

Uso: python -m pipeline.cvm
"""

import io
import zipfile
from pathlib import Path

import pandas as pd
import requests

RAIZ = Path(__file__).resolve().parent.parent
RAW = RAIZ / "data" / "raw" / "cvm"
OUT = RAIZ / "data" / "processed"
URL = "https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/DFP/DADOS/dfp_cia_aberta_{ano}.zip"

CNPJ_CVC = "10.760.260/0001-19"
CONTAS = {
    "3.01": "receita_liquida",
    "3.03": "resultado_bruto",
    "3.05": "ebit",
    "3.11": "lucro_liquido",
}


def dre(ano: int) -> pd.DataFrame | None:
    destino = RAW / f"dfp_{ano}.zip"
    if not destino.exists():
        r = requests.get(URL.format(ano=ano), timeout=300)
        if r.status_code == 404:
            return None
        r.raise_for_status()
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_bytes(r.content)
    with zipfile.ZipFile(destino) as z:
        nome = f"dfp_cia_aberta_DRE_con_{ano}.csv"
        if nome not in z.namelist():
            return None
        df = pd.read_csv(io.BytesIO(z.read(nome)), sep=";", encoding="latin-1", dtype=str)
    df = df[(df["CNPJ_CIA"] == CNPJ_CVC) & (df["ORDEM_EXERC"] == "ÚLTIMO") & df["CD_CONTA"].isin(CONTAS)]
    if df.empty:
        return None
    # reapresentações: fica a versão mais recente entregue
    df = df[df["VERSAO"] == df["VERSAO"].max()]
    linha = {CONTAS[c]: float(v) for c, v in zip(df["CD_CONTA"], df["VL_CONTA"])}
    return pd.DataFrame([{"ano": ano, **linha}])


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    partes = [d for ano in range(2011, 2027) if (d := dre(ano)) is not None]
    df = pd.concat(partes, ignore_index=True)
    df["margem_bruta"] = df["resultado_bruto"] / df["receita_liquida"]
    df["margem_ebit"] = df["ebit"] / df["receita_liquida"]
    df["margem_liquida"] = df["lucro_liquido"] / df["receita_liquida"]
    df.to_csv(OUT / "cvm_cvc.csv", index=False)
    print(df.round(3).to_string())


if __name__ == "__main__":
    main()
