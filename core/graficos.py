"""Padrão visual dos gráficos (Plotly): paleta fixa, linhas finas, grade discreta."""

import plotly.graph_objects as go
import plotly.io as pio

# Paleta categórica validada (ordem fixa: a cor segue a entidade, nunca a posição)
CORES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]
DESTAQUE = CORES[0]   # CNAE 79 / série principal
CONTEXTO = "#b9b8b2"  # demais setores, cinza recessivo
TEXTO = "#14213D"
TEXTO_2 = "#52514e"

pio.templates["rivalidade"] = go.layout.Template(
    layout=dict(
        font=dict(family="Source Sans Pro, sans-serif", size=13, color=TEXTO),
        colorway=CORES,
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=10, r=10, t=40, b=10),
        hovermode="x unified",
        hoverlabel=dict(bgcolor="white", font_size=13),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, title_text=""),
        xaxis=dict(showgrid=False, linecolor="#d6d5d0", ticks="outside", tickcolor="#d6d5d0",
                   title_font=dict(color=TEXTO_2)),
        yaxis=dict(gridcolor="#eceae4", zeroline=False, title_font=dict(color=TEXTO_2)),
        separators=",.",
    ),
    data=dict(
        scatter=[go.Scatter(line=dict(width=2), marker=dict(size=8))],
        bar=[go.Bar(marker=dict(line=dict(width=0), cornerradius=4))],
    ),
)
pio.templates.default = "plotly+rivalidade"

# Eventos marcantes do setor, usados como anotações nas séries temporais
EVENTOS = {
    "2015-01-01": "Recessão 2015-16",
    "2020-03-01": "Pandemia",
    "2023-08-01": "Crise 123milhas",
}


def marcar_eventos(fig, anual: bool = False):
    for data, rotulo in EVENTOS.items():
        x = int(data[:4]) if anual else data
        fig.add_vline(x=x, line=dict(color="#9a9893", width=1, dash="dot"))
        fig.add_annotation(x=x, y=1, yref="paper", text=rotulo, showarrow=False,
                           xanchor="left", yanchor="top", font=dict(size=11, color=TEXTO_2), xshift=3)
    return fig


def brl(valor: float, casas: int = 1) -> str:
    """Formata reais em mil (padrão IBGE/CVM) como texto legível: R$ 17,3 bi."""
    reais = valor * 1000
    for limite, sufixo in [(1e9, "bi"), (1e6, "mi"), (1e3, "mil")]:
        if abs(reais) >= limite:
            return f"R$ {reais / limite:,.{casas}f} {sufixo}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {reais:,.0f}"


def num(valor: float, casas: int = 0) -> str:
    return f"{valor:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def pct(valor: float, casas: int = 1) -> str:
    return f"{valor * 100:,.{casas}f}%".replace(".", ",")
