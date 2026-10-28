# Rivalidade no setor de Agências de Viagem (CNAE 79)

Portal interativo de análise da rivalidade entre agências de viagem e operadoras turísticas no Brasil.

**AP1 – Estratégia Empresarial · Prof. Paulo Tostes · Ibmec**
Autor: Caio Araujo da Luz

## Estrutura

- `app.py`: ponto de entrada do Streamlit (navegação entre páginas)
- `paginas/`: uma página por etapa da análise
- `core/`: carregamento de dados, componentes visuais e registro de fontes
- `pipeline/`: scripts que baixam e tratam os dados das fontes oficiais
- `data/processed/`: dados já tratados, lidos pelo portal

## Rodar localmente

```bash
pip install -r requirements.txt
streamlit run app.py
```
