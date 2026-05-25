"""Gráficos Plotly — visual avançado (gradientes, área, hover unificado)."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

from .chart_theme import (
    GRADIENT_BLUES,
    GRADIENT_WARM,
    donut_center_annotation,
    empty_figure,
    finalize,
    gradient_bar_colors,
    palette_categorical,
)
from .styling import (
    TEXT_SECONDARY,
    THEME_BLUE,
    THEME_BLUE_LIGHT,
    THEME_BLUE_MEDIUM,
    THEME_GREEN,
    THEME_RED,
    THEME_YELLOW,
    WHITE,
)


def monthly_chart(monthly_df: pd.DataFrame) -> go.Figure:
    if monthly_df.empty:
        return empty_figure()

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=monthly_df["mes_dt"],
            y=monthly_df["casos"],
            name="Eventos",
            marker=dict(
                color=monthly_df["casos"],
                colorscale=GRADIENT_BLUES,
                line=dict(color=WHITE, width=0.5),
                cornerradius=6,
            ),
            opacity=0.92,
            hovertemplate="<b>%{x|%b/%Y}</b><br>Eventos: <b>%{y}</b><extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=monthly_df["mes_dt"],
            y=monthly_df["media_movel_3m"],
            name="Média móvel (3 meses)",
            mode="lines+markers",
            line=dict(color=THEME_YELLOW, width=3, shape="spline", smoothing=1.1),
            marker=dict(
                size=8,
                color=THEME_YELLOW,
                line=dict(color=WHITE, width=2),
                symbol="circle",
            ),
            fill="tozeroy",
            fillcolor="rgba(244,185,66,0.2)",
            hovertemplate="<b>%{x|%b/%Y}</b><br>Média móvel: <b>%{y:.1f}</b><extra></extra>",
        )
    )
    fig = finalize(fig, height=360, legend_below=True, margin_r=20)
    fig.update_layout(barmode="overlay", bargap=0.28)
    fig.update_xaxes(tickformat="%b/%Y", type="date")
    return fig


def cid_donut(block_df: pd.DataFrame) -> go.Figure:
    if block_df.empty:
        return empty_figure()

    colors = palette_categorical(len(block_df))
    labels = [f"{r['cid_block']}" for _, r in block_df.iterrows()]
    custom = [str(r["cid_block_name"]) for _, r in block_df.iterrows()]

    fig = go.Figure(
        go.Pie(
            labels=labels,
            values=block_df["casos"],
            hole=0.68,
            marker=dict(colors=colors, line=dict(color=WHITE, width=3)),
            textinfo="percent",
            textposition="inside",
            insidetextorientation="horizontal",
            textfont=dict(size=11, color=WHITE, family="Sora, sans-serif"),
            customdata=custom,
            hovertemplate="<b>%{label}</b><br>%{customdata}<br><b>%{value}</b> casos (%{percent})<extra></extra>",
            pull=[0.02] * len(block_df),
        )
    )
    total = int(block_df["casos"].sum())
    fig = finalize(fig, height=380, margin_r=120)
    fig.update_layout(
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.01,
            font=dict(size=11, color=TEXT_SECONDARY),
        ),
        annotations=donut_center_annotation(total, "casos"),
    )
    return fig


def cid_top_bar(top_df: pd.DataFrame) -> go.Figure:
    if top_df.empty:
        return empty_figure()

    df_sorted = top_df.sort_values("casos")
    labels = [f"{row['cid_group']} · {str(row['cid_name'])[:36]}" for _, row in df_sorted.iterrows()]
    colors = gradient_bar_colors(df_sorted["casos"].tolist(), GRADIENT_BLUES)

    fig = go.Figure(
        go.Bar(
            y=labels,
            x=df_sorted["casos"],
            orientation="h",
            marker=dict(color=colors, line=dict(color=WHITE, width=0.5), cornerradius=4),
            text=df_sorted["casos"],
            textposition="outside",
            textfont=dict(size=11, color=THEME_BLUE, family="Sora, sans-serif"),
            hovertemplate="<b>%{y}</b><br>Casos: <b>%{x}</b><extra></extra>",
        )
    )
    return finalize(fig, height=max(260, 42 * len(top_df) + 70), margin_r=50)


def cargo_bar(cargo_df: pd.DataFrame) -> go.Figure:
    if cargo_df.empty:
        return empty_figure()

    df_sorted = cargo_df.sort_values("casos")
    colors = gradient_bar_colors(df_sorted["casos"].tolist(), GRADIENT_BLUES)

    fig = go.Figure(
        go.Bar(
            y=df_sorted["cargo"],
            x=df_sorted["casos"],
            orientation="h",
            marker=dict(color=colors, line=dict(color=WHITE, width=0.5), cornerradius=4),
            text=df_sorted["casos"],
            textposition="outside",
            textfont=dict(size=11, color=THEME_BLUE, family="Sora, sans-serif"),
            hovertemplate="<b>%{y}</b><br>Eventos: <b>%{x}</b><extra></extra>",
        )
    )
    return finalize(fig, height=max(260, 48 * len(cargo_df) + 60), margin_r=50)


def cargo_dias_bar(cargo_df: pd.DataFrame) -> go.Figure:
    if cargo_df.empty:
        return empty_figure()

    df_sorted = cargo_df.sort_values("media_dias")
    colors = gradient_bar_colors(df_sorted["media_dias"].tolist(), GRADIENT_WARM)

    fig = go.Figure(
        go.Bar(
            y=df_sorted["cargo"],
            x=df_sorted["media_dias"].round(1),
            orientation="h",
            marker=dict(color=colors, line=dict(color=WHITE, width=0.5), cornerradius=4),
            text=[f"{x:.1f}d" for x in df_sorted["media_dias"]],
            textposition="outside",
            textfont=dict(size=11, color=THEME_BLUE, family="Sora, sans-serif"),
            hovertemplate="<b>%{y}</b><br>Média: <b>%{x:.1f}</b> dias<extra></extra>",
        )
    )
    return finalize(fig, height=max(260, 48 * len(cargo_df) + 60), margin_r=55)


def age_bar(age_df: pd.DataFrame) -> go.Figure:
    if age_df.empty:
        return empty_figure()

    colors = gradient_bar_colors(age_df["casos"].tolist(), GRADIENT_BLUES)
    fig = go.Figure(
        go.Bar(
            x=age_df["faixa_etaria"],
            y=age_df["casos"],
            marker=dict(color=colors, line=dict(color=WHITE, width=0.5), cornerradius=6),
            text=age_df["casos"],
            textposition="outside",
            textfont=dict(size=11, color=THEME_BLUE, family="Sora, sans-serif"),
            hovertemplate="<b>%{x}</b><br>Casos: <b>%{y}</b><extra></extra>",
        )
    )
    return finalize(fig, height=300)


def duration_pie(dur_df: pd.DataFrame) -> go.Figure:
    if dur_df.empty:
        return empty_figure()

    colors = palette_categorical(len(dur_df))
    fig = go.Figure(
        go.Pie(
            labels=dur_df["duracao_categoria"],
            values=dur_df["casos"],
            hole=0.58,
            marker=dict(colors=colors, line=dict(color=WHITE, width=2)),
            textinfo="label+percent",
            textfont=dict(size=10, family="Inter, sans-serif"),
            hovertemplate="<b>%{label}</b><br><b>%{value}</b> (%{percent})<extra></extra>",
            pull=[0.03] * len(dur_df),
        )
    )
    fig = finalize(fig, height=320, margin_r=20)
    fig.update_layout(showlegend=True, legend=dict(orientation="h", y=-0.12, x=0))
    return fig


def regional_bar(regional_df: pd.DataFrame, top_n: int = 10) -> go.Figure:
    if regional_df.empty:
        return empty_figure()

    df_sorted = regional_df.head(top_n).sort_values("eventos")
    color_map = {
        "CRÍTICO": THEME_RED,
        "ALTO": "#dd6b20",
        "MÉDIO": THEME_YELLOW,
        "BAIXO": THEME_GREEN,
    }
    colors = [color_map.get(r, THEME_BLUE_MEDIUM) for r in df_sorted["risco"]]

    fig = go.Figure(
        go.Bar(
            y=df_sorted["regional"],
            x=df_sorted["eventos"],
            orientation="h",
            marker=dict(color=colors, line=dict(color=WHITE, width=0.5), cornerradius=4),
            text=df_sorted["eventos"],
            textposition="outside",
            textfont=dict(size=11, color=THEME_BLUE, family="Sora, sans-serif"),
            customdata=df_sorted[["dias", "risco", "media_dias"]].values,
            hovertemplate=(
                "<b>%{y}</b><br>Eventos: <b>%{x}</b><br>"
                "Dias: %{customdata[0]}<br>Risco: %{customdata[1]}<br>"
                "Média: %{customdata[2]:.1f}d<extra></extra>"
            ),
        )
    )
    return finalize(fig, height=max(300, 36 * len(df_sorted) + 70), margin_r=50)
