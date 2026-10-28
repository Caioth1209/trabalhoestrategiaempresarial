import streamlit as st

from core.dados import cnpj79, cvc, entrada_saida, pas_agencias
from core.graficos import num, pct
from core.ui import cabecalho, citar

cabecalho("Conclusões", "Qual é o nível de rivalidade no setor de agências de viagens?")

ag = pas_agencias().set_index("ano")
c = cvc().dropna(subset=["participacao"]).set_index("ano")
base = cnpj79()
ativas = base[base["ativa"]]
es = entrada_saida().set_index("ano")
taxa_media = es.loc[2016:2025, "taxa_entrada"].mean()

st.success("**Diagnóstico: rivalidade ALTA e crescente.** O setor tem muitos concorrentes pequenos, "
           "barreiras de entrada baixas, uma líder perdendo espaço e margens sendo comprimidas.", icon="🎯")

st.subheader("Evidências")
st.markdown(f"""
| Fator de rivalidade | O que os dados mostram | Leitura |
|---|---|---|
| **Concentração** | A líder (CVC) tem {pct(c['participacao'].iloc[-1])} da receita do setor em {c.index[-1]}, abaixo do pico de {pct(c['participacao'].max())} em {c['participacao'].idxmax()}. O HHI é muito baixo. | Mercado fragmentado e sem líder dominante |
| **Número e porte dos concorrentes** | {num(len(ativas))} empresas ativas, das quais {pct(ativas['porte'].eq('01').mean())} são microempresas e {pct(ativas['mei'].mean())} são MEI. Média de {num(ag['pessoas_por_empresa'].iloc[-1], 1)} pessoas por empresa. | Muitos concorrentes de tamanho parecido |
| **Barreiras de entrada** | Cerca de {pct(taxa_media)} de novas empresas por ano em relação ao estoque (2016-2025), acima da mediana dos setores. Mais da metade dos entrantes recentes é MEI. | Entrar é barato e fácil |
| **Crescimento do mercado** | A receita real caiu à metade em 2020 e só superou o nível de 2019 em 2023. | Disputa por uma demanda que ficou anos parada |
| **Preços e margens** | O valor adicionado caiu de {pct(ag.loc[2019, 'va_sobre_receita'])} para {pct(ag['va_sobre_receita'].iloc[-1])} da receita entre 2019 e {ag.index[-1]}. A CVC teve prejuízo de 2019 a 2025. | Pressão forte sobre comissões e rentabilidade |
| **Diferenciação** | O produto (passagem, hotel, pacote) é o mesmo em qualquer canal, e o cliente compara preços online em segundos. | Baixo custo de troca para o cliente |
""")

st.subheader("Desafios para as empresas")
st.markdown("""
- **Competição direta com OTAs e com os próprios fornecedores**: companhias aéreas e hotéis vendem direto
  ao consumidor e reduzem o espaço da intermediação.
- **Margens comprimidas**: comissões menores e mais concorrentes por cliente tornam a escala decisiva.
- **Confiança do consumidor**: a quebra da 123milhas e a crise do Hurb em 2023 deixaram o cliente desconfiado
  de venda antecipada com entrega futura.
- **Sazonalidade forte**: a demanda concentra-se em dezembro, janeiro e julho, e a disputa por clientes fica
  mais acirrada nos meses fracos.
""")

st.subheader("Oportunidades")
st.markdown("""
- **Nichos e especialização** (turismo de experiência, corporativo, eventos, destinos específicos), onde
  o atendimento consultivo vale mais que o preço.
- **Consolidação**: com milhares de micro agências, há espaço para redes, franquias e plataformas que deem
  escala aos pequenos.
- **Tecnologia e dados**: personalização, pacotes dinâmicos e pós-venda podem reduzir a guerra de preços.
- **Demanda em alta**: o volume do turismo está acima do nível pré-pandemia, o que abre espaço para crescer
  sem depender só de tirar clientes dos rivais.
""")

citar("pas", "cvm", "cnpj", "cempre", "pms")
