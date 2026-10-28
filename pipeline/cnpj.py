"""Coleta e tratamento dos Dados Abertos do CNPJ (Receita Federal).

Gera em data/processed:
- cnpj_estab_79.parquet : estabelecimentos com CNAE principal da divisão 79
- cnpj_empresas_79.parquet : porte, capital social e razão social dessas empresas
- cnpj_simples_79.parquet : opção pelo Simples/MEI dessas empresas
- cnpj_divisoes.csv : aberturas/encerramentos/ativos por divisão CNAE (2 dígitos) e ano,
  usado no comparativo com outros setores

Uso: python -m pipeline.cnpj [AAAA-MM]
"""

import io
import sys
import zipfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pandas as pd
import requests

RAIZ = Path(__file__).resolve().parent.parent
RAW = RAIZ / "data" / "raw" / "cnpj"
OUT = RAIZ / "data" / "processed"

SHARE = "gn672Ad4CF8N6TK"
BASE = "https://arquivos.receitafederal.gov.br/public.php/webdav/Dados/Cadastros/CNPJ"

COLS_ESTAB = {
    0: "cnpj_basico", 1: "cnpj_ordem", 2: "cnpj_dv", 3: "matriz_filial",
    5: "situacao", 6: "data_situacao", 7: "motivo_situacao",
    10: "data_inicio", 11: "cnae", 19: "uf", 20: "municipio",
}
COLS_EMPRESA = {0: "cnpj_basico", 1: "razao_social", 2: "natureza_juridica",
                4: "capital_social", 5: "porte"}
COLS_SIMPLES = {0: "cnpj_basico", 1: "opcao_simples", 2: "data_opcao_simples",
                3: "data_exclusao_simples", 4: "opcao_mei", 5: "data_opcao_mei",
                6: "data_exclusao_mei"}


def baixar(mes: str, nome: str) -> Path:
    destino = RAW / mes / nome
    if destino.exists():
        return destino
    destino.parent.mkdir(parents=True, exist_ok=True)
    tmp = destino.with_suffix(".part")
    for tentativa in range(5):
        try:
            with requests.get(f"{BASE}/{mes}/{nome}", auth=(SHARE, ""), stream=True, timeout=120) as r:
                r.raise_for_status()
                with open(tmp, "wb") as f:
                    for bloco in r.iter_content(1 << 20):
                        f.write(bloco)
            tmp.rename(destino)
            print(f"baixado {nome}", flush=True)
            return destino
        except requests.RequestException as e:
            print(f"falha {nome} ({tentativa + 1}/5): {e}", flush=True)
    raise RuntimeError(f"não foi possível baixar {nome}")


def ler_zip(caminho: Path, colunas: dict, chunksize=1_000_000):
    with zipfile.ZipFile(caminho) as z:
        with z.open(z.namelist()[0]) as f:
            texto = io.TextIOWrapper(f, encoding="latin-1")
            yield from pd.read_csv(
                texto, sep=";", header=None, dtype=str, usecols=list(colunas),
                chunksize=chunksize, quotechar='"', keep_default_na=False,
            )


def ano(serie: pd.Series) -> pd.Series:
    return pd.to_numeric(serie.str[:4], errors="coerce")


def processar_estab(caminho: Path):
    filtrados, agregados = [], []
    for df in ler_zip(caminho, COLS_ESTAB):
        df = df.rename(columns=COLS_ESTAB)
        df["divisao"] = df["cnae"].str[:2]
        matriz = df[df["matriz_filial"] == "1"]
        abert = matriz.groupby([matriz["divisao"], ano(matriz["data_inicio"]).rename("ano")]).size().rename("aberturas")
        baix = matriz[matriz["situacao"] == "08"]
        fech = baix.groupby([baix["divisao"], ano(baix["data_situacao"]).rename("ano")]).size().rename("encerramentos")
        ativ = matriz[matriz["situacao"] == "02"].groupby("divisao").size().rename("ativas_hoje")
        agregados.append((abert, fech, ativ))
        filtrados.append(df[df["divisao"] == "79"].drop(columns="divisao"))
    caminho.unlink()  # libera disco
    return pd.concat(filtrados), agregados


def main(mes: str):
    OUT.mkdir(parents=True, exist_ok=True)
    nomes = [f"Estabelecimentos{i}.zip" for i in range(10)]

    estab, abert, fech, ativ = [], [], [], []
    with ThreadPoolExecutor(4) as ex:
        for caminho in ex.map(lambda n: baixar(mes, n), nomes):
            filtrado, agregados = processar_estab(caminho)
            estab.append(filtrado)
            for a, f, t in agregados:
                abert.append(a), fech.append(f), ativ.append(t)
            print(f"processado {caminho.name}: {len(filtrado)} estabelecimentos CNAE 79", flush=True)

    estab = pd.concat(estab, ignore_index=True)
    estab.to_parquet(OUT / "cnpj_estab_79.parquet", index=False)

    a = pd.concat(abert).groupby(level=[0, 1]).sum()
    f = pd.concat(fech).groupby(level=[0, 1]).sum()
    divisoes = pd.concat([a, f], axis=1).fillna(0).astype(int).reset_index()
    t = pd.concat(ativ).groupby(level=0).sum().rename("ativas_hoje")
    divisoes = divisoes.merge(t, left_on="divisao", right_index=True, how="left")
    divisoes.to_csv(OUT / "cnpj_divisoes.csv", index=False)

    basicos = set(estab["cnpj_basico"])
    empresas, simples = [], []
    nomes = [f"Empresas{i}.zip" for i in range(10)] + ["Simples.zip"]
    with ThreadPoolExecutor(4) as ex:
        for caminho in ex.map(lambda n: baixar(mes, n), nomes):
            cols = COLS_SIMPLES if caminho.name == "Simples.zip" else COLS_EMPRESA
            destino = simples if caminho.name == "Simples.zip" else empresas
            for df in ler_zip(caminho, cols):
                df = df.rename(columns=cols)
                destino.append(df[df["cnpj_basico"].isin(basicos)])
            caminho.unlink()
            print(f"processado {caminho.name}", flush=True)

    emp = pd.concat(empresas, ignore_index=True)
    emp["capital_social"] = pd.to_numeric(emp["capital_social"].str.replace(",", "."), errors="coerce")
    emp.to_parquet(OUT / "cnpj_empresas_79.parquet", index=False)
    pd.concat(simples, ignore_index=True).to_parquet(OUT / "cnpj_simples_79.parquet", index=False)
    print("concluído", flush=True)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "2026-10")
