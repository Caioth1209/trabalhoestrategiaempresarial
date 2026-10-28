import streamlit as st

from core.fontes import FONTES
from core.ui import cabecalho

cabecalho("Fontes e metodologia", "De onde vêm os dados e como foram tratados")

st.subheader("Fontes")
for f in FONTES.values():
    with st.container(border=True):
        st.markdown(f"**[{f['nome']}]({f['url']})**  \n{f['uso']}")

st.subheader("Variáveis usadas para medir a rivalidade")
st.markdown("""
| Dimensão (Porter) | Indicador | Fonte |
|---|---|---|
| Concentração | Participação da líder (CR1) e HHI mínimo | CVM + PAS |
| Número e tamanho dos concorrentes | Empresas, pessoas por empresa, porte, MEI | PAS, CEMPRE, CNPJ |
| Barreiras de entrada e saída | Aberturas, baixas, taxas de entrada e saída, sobrevivência | CNPJ |
| Crescimento do mercado | Receita real, índice de volume do turismo | PAS, PMS, IPCA |
| Pressão sobre preços e margens | Valor adicionado ÷ receita, preço implícito, margens da CVC | PAS, PMS, CVM |
| Comparação com a economia | Rankings e agrupamento entre atividades de serviço | PAS, CNPJ |
""")

st.subheader("Tratamento dos dados")
st.markdown("""
- **Coleta automatizada em Python** (pasta `pipeline/` do repositório): cada fonte tem um script que baixa
  os arquivos oficiais e gera tabelas limpas em `data/processed/`.
- **PAS**: a Tabela 1 de cada edição (2011–2023) foi lida das planilhas do FTP do IBGE. Quando a edição
  traz dois anos, fica só o ano de referência.
- **CNPJ**: dos cerca de 60 milhões de estabelecimentos do cadastro, foram filtradas as matrizes com CNAE
  principal 7911-2, 7912-1 ou 7990-2 e cruzadas com as tabelas de empresas (porte) e do Simples (MEI).
- **Valores reais**: deflacionados pela média anual do IPCA, a preços do último ano completo.
- **Preço implícito do turismo**: índice de receita nominal ÷ índice de volume (PMS).
""")

st.subheader("Limitações")
st.markdown("""
- **Não há market share público por empresa.** A concentração é estimada pela receita da CVC (única
  companhia aberta do setor) dividida pela receita da CNAE 79 na PAS. Decolar, 123milhas, Hurb e outras não
  publicam balanço no Brasil.
- **A receita consolidada da CVC inclui operações no exterior** em parte do período, o que pode
  superestimar levemente a participação dela no Brasil.
- **A PAS é divulgada com cerca de dois anos de atraso** (último ano: 2023).
- **O CEMPRE mudou de metodologia em 2022** e passou a captar mais empresas pequenas, o que cria um degrau
  na série de número de empresas.
- **O cadastro do CNPJ é uma fotografia atual**: empresas que mudaram de CNAE aparecem com a CNAE de hoje,
  e as inaptas ou suspensas não contam como baixas.
""")
