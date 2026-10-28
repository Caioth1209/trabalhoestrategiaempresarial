"""Registro central das fontes de dados usadas no portal."""

FONTES = {
    "pas": {
        "nome": "IBGE – Pesquisa Anual de Serviços (PAS)",
        "url": "https://www.ibge.gov.br/estatisticas/economicas/servicos/9028-pesquisa-anual-de-servicos.html",
        "uso": "Receita operacional líquida, valor adicionado, salários, pessoal ocupado e número de empresas "
               "por atividade de serviço, 2011-2023 (Tabela 1 de cada edição, via FTP do IBGE).",
    },
    "pms": {
        "nome": "IBGE – Pesquisa Mensal de Serviços (PMS)",
        "url": "https://sidra.ibge.gov.br/tabela/8694",
        "uso": "Índices mensais de volume e de receita nominal das atividades turísticas (SIDRA 8694) "
               "e de volume por atividade de serviço (SIDRA 8688), 2011 em diante.",
    },
    "cempre": {
        "nome": "IBGE – Cadastro Central de Empresas (CEMPRE)",
        "url": "https://sidra.ibge.gov.br/tabela/9418",
        "uso": "Empresas, pessoal ocupado e salários por divisão e classe CNAE, 2006-2024 (SIDRA 6449 e 9418).",
    },
    "cnpj": {
        "nome": "Receita Federal – Dados Abertos do CNPJ",
        "url": "https://dados.gov.br/dados/conjuntos-dados/cadastro-nacional-da-pessoa-juridica---cnpj",
        "uso": "Cadastro de todos os estabelecimentos do país (edição out/2026): datas de abertura e baixa, "
               "UF, porte e opção pelo Simples/MEI das empresas das CNAEs 7911-2, 7912-1 e 7990-2.",
    },
    "cvm": {
        "nome": "CVM – Demonstrações Financeiras Padronizadas (DFP)",
        "url": "https://dados.cvm.gov.br/dataset/cia_aberta-doc-dfp",
        "uso": "DRE consolidada da CVC Brasil (única companhia aberta da CNAE 79), 2012-2025.",
    },
    "ipca": {
        "nome": "IBGE – IPCA",
        "url": "https://sidra.ibge.gov.br/tabela/1737",
        "uso": "Deflator para expressar valores monetários a preços constantes (média anual).",
    },
}
