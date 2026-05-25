"""Tema avançado e helpers para gráficos Plotly."""

from __future__ import annotations

from typing import Iterable, Sequence

import plotly.graph_objects as go

from .styling import (
    LIGHT_BORDER,
    OFF_WHITE,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    THEME_BLUE,
    THEME_BLUE_ACCENT,
    THEME_BLUE_DARK,
    THEME_BLUE_LIGHT,
    THEME_BLUE_MEDIUM,
    THEME_GREEN,
    THEME_RED,
    THEME_YELLOW,
    WHITE,
    plotly_layout,
)

PLOTLY_CONFIG = {
    "displayModeBar": True,
    "displaylogo": False,
    "modeBarButtonsToRemove": [
        "lasso2d",
        "select2d",
        "autoScale2d",
        "toggleSpikelines",
    ],
    "toImageButtonOptions": {
        "format": "png",
        "filename": "planilha-painel-grafico",
        "height": 800,
        "width": 1200,
        "scale": 2,
    },
    "responsive": True,
}

GRADIENT_BLUES = [
    [0.0, "#dbeafe"],
    [0.35, THEME_BLUE_LIGHT],
    [0.7, THEME_BLUE_MEDIUM],
    [1.0, THEME_BLUE_DARK],
]

GRADIENT_WARM = [
    [0.0, "#fef3c7"],
    [0.5, THEME_YELLOW],
    [1.0, "#d97706"],
]


def gradient_bar_colors(values: Sequence[float], colorscale: list | None = None) -> list[str]:
    """Interpola cores ao longo dos valores (para barras horizontais)."""
    if not values:
        return []
    cs = colorscale or GRADIENT_BLUES
    vmin, vmax = min(values), max(values)
    span = vmax - vmin or 1.0
    out: list[str] = []
    for v in values:
        t = (float(v) - vmin) / span
        # amostra simples nos stops da colorscale Plotly
        if t <= cs[0][0]:
            out.append(cs[0][1])
            continue
        for i in range(1, len(cs)):
            if t <= cs[i][0]:
                out.append(cs[i][1])
                break
        else:
            out.append(cs[-1][1])
    return out


def empty_figure(message: str = "Sem dados no período filtrado") -> go.Figure:
    fig = go.Figure()
    layout = plotly_layout()
    layout["height"] = 280
    layout["annotations"] = [
        {
            "text": message,
            "xref": "paper",
            "yref": "paper",
            "x": 0.5,
            "y": 0.5,
            "showarrow": False,
            "font": {"size": 14, "color": TEXT_SECONDARY, "family": "Inter, sans-serif"},
        }
    ]
    layout["xaxis"]["visible"] = False
    layout["yaxis"]["visible"] = False
    fig.update_layout(**layout)
    return fig


def finalize(
    fig: go.Figure,
    *,
    height: int = 320,
    title: str | None = None,
    legend_below: bool = False,
    margin_r: int = 30,
) -> go.Figure:
    layout = plotly_layout(title)
    layout["height"] = height
    layout["hovermode"] = "x unified"
    layout["hoverlabel"] = {
        "bgcolor": THEME_BLUE_DARK,
        "bordercolor": THEME_BLUE_MEDIUM,
        "font": {"color": "#ffffff", "family": "Inter, sans-serif", "size": 12},
    }
    layout["margin"] = {"l": 52, "r": margin_r, "t": 48 if title else 28, "b": 48}
    layout["paper_bgcolor"] = OFF_WHITE
    layout["plot_bgcolor"] = WHITE
    layout["uirevision"] = "planilha-painel"
    if legend_below:
        layout["legend"].update(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor=LIGHT_BORDER,
            borderwidth=1,
        )
    fig.update_layout(**layout)
    fig.update_xaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor="rgba(221,229,240,0.9)",
        zeroline=False,
        linecolor=LIGHT_BORDER,
        tickfont=dict(size=11, color=TEXT_SECONDARY),
    )
    fig.update_yaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor="rgba(221,229,240,0.9)",
        zeroline=False,
        linecolor=LIGHT_BORDER,
        tickfont=dict(size=11, color=TEXT_SECONDARY),
    )
    return fig


def donut_center_annotation(total: int, subtitle: str = "registros") -> list[dict]:
    return [
        {
            "text": f"<b>{total}</b><br><span style='font-size:11px;color:{TEXT_SECONDARY}'>{subtitle}</span>",
            "x": 0.5,
            "y": 0.5,
            "font": {"size": 26, "color": THEME_BLUE, "family": "Sora, sans-serif"},
            "showarrow": False,
        }
    ]


def palette_categorical(n: int) -> list[str]:
    base = [
        THEME_BLUE,
        THEME_BLUE_MEDIUM,
        THEME_BLUE_LIGHT,
        THEME_BLUE_ACCENT,
        THEME_YELLOW,
        THEME_GREEN,
        THEME_RED,
        "#7c5cbf",
        "#0891b2",
        "#9b6b3f",
        "#6b7280",
    ]
    return [base[i % len(base)] for i in range(n)]
