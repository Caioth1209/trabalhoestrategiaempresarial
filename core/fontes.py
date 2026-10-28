"""Registro central das fontes de dados usadas no portal."""

FONTES = {
    "pas": {
        "nome": "IBGE – Pesquisa Anual de Serviços (PAS)",
        "orgao": "IBGE",
        "url": "https://www.ibge.gov.br/estatisticas/economicas/servicos/9028-pesquisa-anual-de-servicos.html",
        "uso": "Receita, número de empresas e pessoal ocupado da CNAE 79 e de outros serviços.",
    },
    "pms": {
        "nome": "IBGE – Pesquisa Mensal de Serviços (PMS)",
        "orgao": "IBGE",
        "url": "https://www.ibge.gov.br/estatisticas/economicas/servicos/9229-pesquisa-mensal-de-servicos.html",
        "uso": "Índice de volume das atividades turísticas (série mensal).",
    },
    "cnpj": {
        "nome": "Receita Federal – Dados Abertos do CNPJ",
        "orgao": "Receita Federal",
        "url": "https://dados.gov.br/dados/conjuntos-dados/cadastro-nacional-da-pessoa-juridica---cnpj",
        "uso": "Abertura e encerramento de empresas das CNAEs 7911-2 e 7912-1, por ano, UF e porte.",
    },
    "cvm": {
        "nome": "CVM – Demonstrações Financeiras de Companhias Abertas",
        "orgao": "CVM",
        "url": "https://dados.cvm.gov.br/dataset/cia_aberta-doc-dfp",
        "uso": "Receita e margens das empresas listadas do setor (ex.: CVC Brasil).",
    },
}
