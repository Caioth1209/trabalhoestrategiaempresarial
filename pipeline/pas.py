"""Coleta da Pesquisa Anual de Serviços (IBGE) – Tabela 1 de cada edição.

A Tabela 1 traz, por atividade de serviço: receita operacional líquida, valor adicionado,
salários, pessoal ocupado e número de empresas. Usamos a linha de agências de viagens
(CNAE 79) e as demais atividades para o comparativo setorial.

Gera data/processed/pas_atividades.csv (ano, atividade, variáveis em R$ mil / unidades).

Uso: python -m pipeline.pas
"""

import io
import re
import unicodedata
import zipfile
from pathlib import Path

import pandas as pd
import requests

RAIZ = Path(__file__).resolve().parent.parent
RAW = RAIZ / "data" / "raw" / "pas"
OUT = RAIZ / "data" / "processed"
FTP = "https://ftp.ibge.gov.br/Comercio_e_Servicos/Pesquisa_Anual_de_Servicos"

# ano de referência -> arquivo da edição mais recente que traz aquele ano
ARQUIVOS = {
    2011: "pas2013/xls/pas2013_CNAE_2_0_2011_xls_20230529.zip",
    2012: "pas2013/xls/pas2013_CNAE_2_0_2012_xls_20230529.zip",
    2013: "pas2013/xls/pas2013_CNAE_2_0_2013_xls_20230529.zip",
    2014: "pas2016/xls/tabelas_2014_xls_20230529.zip",
    2015: "pas2016/xls/tabelas_2015_xls_20230529.zip",
    2016: "pas2016/xls/tabelas_2016_xls_20230529.zip",
    2017: "pas2019/xlsx/tabelas_2017_xlsx_20230529.zip",
    2018: "pas2020/xlsx/tabelas_2018_xlsx_20230529.zip",
    2019: "pas2021/xlsx/tabelas_2019_xlsx.zip",
    2020: "pas2022/xlsx/tabelas_2020_xlsx.zip",
    2021: "pas2023/xlsx/tabelas_2021_xlsx.zip",
    2022: "pas2023/xlsx/tabelas_2022_xlsx.zip",
    2023: "pas2023/xlsx/tabelas_2023_xlsx.zip",
}

VARIAVEIS = ["receita_liquida", "valor_adicionado", "salarios", "pessoal_ocupado", "empresas"]


def limpar(texto: str) -> str:
    """Remove notas de rodapé, como "(2)", e espaços repetidos."""
    return re.sub(r"\s+", " ", re.sub(r"\(\d+\)", "", str(texto))).strip()


def chave(texto: str) -> str:
    """Versão sem acentos, estável entre edições, para casar a mesma atividade em anos diferentes."""
    return unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode().lower()


def baixar(caminho: str) -> Path:
    destino = RAW / Path(caminho).name
    if not destino.exists():
        destino.parent.mkdir(parents=True, exist_ok=True)
        r = requests.get(f"{FTP}/{caminho}", timeout=300)
        r.raise_for_status()
        destino.write_bytes(r.content)
    return destino


def tabela1(zip_path: Path) -> pd.DataFrame:
    """Localiza a Tabela 1 dentro do zip e devolve como DataFrame bruto (sem cabeçalho)."""
    with zipfile.ZipFile(zip_path) as z:
        for nome in z.namelist():
            base = Path(nome).name.lower()
            if re.fullmatch(r"(tabela ?0?1|tab0?1)\.xlsx?", base):
                return pd.read_excel(io.BytesIO(z.read(nome)), header=None, sheet_name=None)
    raise FileNotFoundError(f"Tabela 1 não encontrada em {zip_path.name}")


def numero(x):
    if isinstance(x, (int, float)) and not pd.isna(x):
        return float(x)
    s = str(x).strip().replace(" ", "")
    return float(s) if re.fullmatch(r"-?\d+(\.\d+)?", s) else None


def extrair(planilhas: dict, ano: int) -> pd.DataFrame:
    linhas, rotulo_pendente, bloco = [], "", None
    for df in planilhas.values():
        for _, row in df.iterrows():
            valores = row.tolist()
            rotulo = "" if pd.isna(valores[0]) else str(valores[0]).strip()
            if re.fullmatch(r"(19|20)\d{2}", rotulo.split(".")[0]):
                bloco = int(rotulo.split(".")[0])
                rotulo_pendente = ""
                continue
            nums = [n for n in (numero(v) for v in valores[1:]) if n is not None]
            if len(nums) >= 5 and rotulo:
                linhas.append({"ano_bloco": bloco, "atividade": limpar(f"{rotulo_pendente} {rotulo}"),
                               **dict(zip(VARIAVEIS, nums[:5]))})
                rotulo_pendente = ""
            elif rotulo and not nums and not rotulo.lower().startswith(("tabela", "fonte", "nota", "(")):
                rotulo_pendente = f"{rotulo_pendente} {rotulo}".strip()
            else:
                rotulo_pendente = ""
    out = pd.DataFrame(linhas)
    # tabelas recentes trazem dois anos (t-1 e t); fica só o ano de referência
    if out["ano_bloco"].notna().any():
        out = out[out["ano_bloco"] == ano]
    out["ano"] = ano
    return out.drop(columns="ano_bloco").drop_duplicates("atividade")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    partes = []
    for ano, caminho in ARQUIVOS.items():
        df = extrair(tabela1(baixar(caminho)), ano)
        agencias = df[df["atividade"].str.contains("viage", case=False)]
        print(ano, f"{len(df)} atividades", "| agências:", agencias[VARIAVEIS].values.tolist())
        partes.append(df)
    df = pd.concat(partes, ignore_index=True)
    # usa o rótulo da edição mais recente para todos os anos
    df["chave"] = df["atividade"].map(chave)
    rotulos = df.sort_values("ano").groupby("chave")["atividade"].last()
    df["atividade"] = df["chave"].map(rotulos)
    df.to_csv(OUT / "pas_atividades.csv", index=False)


if __name__ == "__main__":
    main()
