import importlib

import streamlit as st

import core.dados
import core.fontes
import core.glossario
import core.graficos
import core.ui

# O Streamlit Cloud atualiza os arquivos a cada push, mas mantém em memória os módulos já
# importados. Recarregar garante que as páginas vejam a versão nova de core/ sem reiniciar o app.
for modulo in (core.glossario, core.fontes, core.graficos, core.dados, core.ui):
    importlib.reload(modulo)

from core.ui import barra_lateral  # noqa: E402

st.set_page_config(
    page_title="Rivalidade · Agências de Viagem",
    page_icon="✈️",
    layout="wide",
)

paginas = {
    "Análise": [
        st.Page("paginas/visao_geral.py", title="Visão geral", icon="🧭", default=True),
        st.Page("paginas/concentracao.py", title="Estrutura e concentração", icon="🏢"),
        st.Page("paginas/entrada_saida.py", title="Entrada e saída", icon="🔁"),
        st.Page("paginas/desempenho.py", title="Desempenho e margens", icon="📈"),
        st.Page("paginas/comparativo.py", title="Comparativo setorial", icon="⚖️"),
    ],
    "Ferramentas": [
        st.Page("paginas/explorador.py", title="Explorador", icon="🎛️"),
        st.Page("paginas/avancada.py", title="Análise avançada", icon="🧪"),
    ],
    "Fechamento": [
        st.Page("paginas/conclusoes.py", title="Conclusões", icon="🎯"),
        st.Page("paginas/fontes.py", title="Fontes e metodologia", icon="📚"),
    ],
}

barra_lateral()
st.navigation(paginas).run()
