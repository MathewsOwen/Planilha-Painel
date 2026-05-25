"""Cálculo de KPIs, agregações, recorrência e classificação de risco."""

from __future__ import annotations

from typing import List, Dict

import numpy as np
import pandas as pd


def kpis(df: pd.DataFrame) -> dict:
    """KPIs principais do dashboard."""
    if df.empty:
        return {
            "total_registros": 0,
            "total_dias": 0,
            "media_dias": 0.0,
            "regionais_criticas": 0,
            "cid_predominante": "—",
            "cid_predominante_nome": "—",
            "cid_predominante_count": 0,
            "servidores_recorrentes": 0,
        }

    total_registros = len(df)
    total_dias = int(df["dias"].fillna(0).sum())
    media_dias = float(df["dias"].dropna().mean()) if df["dias"].notna().any() else 0.0

    by_regional = df.groupby("regional").size().sort_values(ascending=False)
    threshold = max(10, int(by_regional.quantile(0.75))) if len(by_regional) > 4 else 10
    regionais_criticas = int((by_regional >= threshold).sum())

    by_cid = df.groupby("cid_group").size().sort_values(ascending=False)
    if len(by_cid) > 0:
        cid_top = by_cid.index[0]
        cid_top_count = int(by_cid.iloc[0])
        from .loader import CID_NAMES
        cid_top_nome = CID_NAMES.get(cid_top, "—")
    else:
        cid_top = "—"
        cid_top_count = 0
        cid_top_nome = "—"

    recorrencia = recurrence_table(df)
    servidores_recorrentes = int((recorrencia["eventos"] >= 2).sum()) if not recorrencia.empty else 0

    return {
        "total_registros": total_registros,
        "total_dias": total_dias,
        "media_dias": media_dias,
        "regionais_criticas": regionais_criticas,
        "cid_predominante": cid_top,
        "cid_predominante_nome": cid_top_nome,
        "cid_predominante_count": cid_top_count,
        "servidores_recorrentes": servidores_recorrentes,
    }


def regional_summary(df: pd.DataFrame, exclude_unknown: bool = True) -> pd.DataFrame:
    """Agrega por superintendência regional com classificação de risco.

    Se exclude_unknown=True, ignora "Não informado" para o ranking de risco.
    """
    if df.empty:
        return pd.DataFrame(columns=["regional", "eventos", "dias", "media_dias", "cid_top", "risco"])

    base = df[df["regional"] != "Não informado"] if exclude_unknown else df
    if base.empty:
        base = df

    agg = (
        base.groupby("regional")
        .agg(
            eventos=("data_inicio", "size"),
            dias=("dias", "sum"),
            media_dias=("dias", "mean"),
        )
        .reset_index()
    )

    cid_top = (
        base.groupby(["regional", "cid_group"])
        .size()
        .reset_index(name="n")
        .sort_values(["regional", "n"], ascending=[True, False])
        .drop_duplicates("regional")
        .rename(columns={"cid_group": "cid_top"})[["regional", "cid_top"]]
    )
    agg = agg.merge(cid_top, on="regional", how="left")

    q75 = agg["eventos"].quantile(0.75) if len(agg) > 4 else agg["eventos"].max()
    q50 = agg["eventos"].quantile(0.50) if len(agg) > 4 else 0

    def classify(n: float) -> str:
        if n >= max(q75, 12):
            return "CRÍTICO"
        if n >= max(q50, 6):
            return "ALTO"
        if n >= 3:
            return "MÉDIO"
        return "BAIXO"

    agg["risco"] = agg["eventos"].map(classify)
    agg = agg.sort_values("eventos", ascending=False).reset_index(drop=True)
    return agg


def recurrence_table(df: pd.DataFrame) -> pd.DataFrame:
    """Identifica "servidores" recorrentes — agrupa por (regional, lotacao, cargo, idade).

    Como a planilha não tem ID único, usamos a combinação como proxy.
    """
    if df.empty:
        return pd.DataFrame(columns=["regional", "lotacao", "cargo", "idade", "eventos", "dias_totais"])

    key_cols = ["regional", "lotacao", "cargo", "idade"]
    sub = df.dropna(subset=["idade"]).copy()
    if sub.empty:
        return pd.DataFrame(columns=key_cols + ["eventos", "dias_totais"])

    grouped = (
        sub.groupby(key_cols, dropna=False)
        .agg(eventos=("data_inicio", "size"), dias_totais=("dias", "sum"))
        .reset_index()
        .sort_values(["eventos", "dias_totais"], ascending=[False, False])
    )
    return grouped


def cid_breakdown(df: pd.DataFrame, top_n: int = 6) -> pd.DataFrame:
    """Top CIDs (agrupados a 3 dígitos: F32, F41, etc)."""
    if df.empty:
        return pd.DataFrame(columns=["cid_group", "cid_name", "casos", "dias_totais"])
    out = (
        df.dropna(subset=["cid_group"])
        .groupby(["cid_group", "cid_name"])
        .agg(casos=("data_inicio", "size"), dias_totais=("dias", "sum"))
        .reset_index()
        .sort_values("casos", ascending=False)
    )
    return out.head(top_n)


def cid_block_breakdown(df: pd.DataFrame) -> pd.DataFrame:
    """Distribuição por bloco CID (F30-F39, F40-F49, etc)."""
    if df.empty:
        return pd.DataFrame(columns=["cid_block", "cid_block_name", "casos", "pct"])
    out = (
        df.dropna(subset=["cid_block"])
        .groupby(["cid_block", "cid_block_name"])
        .size()
        .reset_index(name="casos")
        .sort_values("casos", ascending=False)
    )
    total = out["casos"].sum()
    out["pct"] = (out["casos"] / total * 100).round(1) if total > 0 else 0
    return out


def cargo_breakdown(df: pd.DataFrame) -> pd.DataFrame:
    """Por cargo com média de dias."""
    if df.empty:
        return pd.DataFrame(columns=["cargo", "casos", "media_dias", "dias_totais"])
    out = (
        df.groupby("cargo")
        .agg(
            casos=("data_inicio", "size"),
            media_dias=("dias", "mean"),
            dias_totais=("dias", "sum"),
        )
        .reset_index()
        .sort_values("casos", ascending=False)
    )
    return out


def monthly_trend(df: pd.DataFrame) -> pd.DataFrame:
    """Série temporal mensal: contagem e dias acumulados."""
    from .loader import _format_mes_pt

    if df.empty:
        return pd.DataFrame(columns=["mes", "mes_label", "casos", "dias", "media_dias"])
    out = (
        df.groupby(df["data_inicio"].dt.to_period("M"))
        .agg(
            casos=("data_inicio", "size"),
            dias=("dias", "sum"),
            media_dias=("dias", "mean"),
        )
        .reset_index()
    )
    out["mes"] = out["data_inicio"].astype(str)
    out["mes_dt"] = out["data_inicio"].dt.to_timestamp()
    out["mes_label"] = out["mes_dt"].apply(_format_mes_pt)
    out["media_movel_3m"] = out["casos"].rolling(3, min_periods=1).mean().round(1)
    return out[["mes", "mes_dt", "mes_label", "casos", "dias", "media_dias", "media_movel_3m"]]


def age_distribution(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["faixa_etaria", "casos"])
    ordering = ["Até 30", "31–40", "41–50", "51–60", "60+", "Não informado"]
    out = df.groupby("faixa_etaria").size().reset_index(name="casos")
    out["ordem"] = out["faixa_etaria"].map(lambda x: ordering.index(x) if x in ordering else 99)
    return out.sort_values("ordem").drop(columns="ordem")


def duration_distribution(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["duracao_categoria", "casos"])
    ordering = ["Curto (1–15d)", "Médio (16–60d)", "Longo (61–180d)", "Muito longo (>180d)", "Não informado"]
    out = df.groupby("duracao_categoria").size().reset_index(name="casos")
    out["ordem"] = out["duracao_categoria"].map(lambda x: ordering.index(x) if x in ordering else 99)
    return out.sort_values("ordem").drop(columns="ordem")


def detect_insights(df: pd.DataFrame) -> List[Dict[str, str]]:
    """Gera 3 insights dinâmicos a partir dos dados."""
    if df.empty:
        return [
            {"num": "—", "label": "Sem dados disponíveis no filtro selecionado."},
        ]

    media = df["dias"].mean()
    media_str = f"{media:.1f} dias".replace(".", ",")

    regional_top = df["regional"].value_counts().head(1)
    regional_label = regional_top.index[0] if len(regional_top) else "—"
    regional_count = int(regional_top.iloc[0]) if len(regional_top) else 0

    cid_top2 = df["cid_group"].value_counts().head(2)
    cid_combo = " + ".join(cid_top2.index.tolist()) if len(cid_top2) else "—"
    cid_pct = (cid_top2.sum() / len(df) * 100) if len(df) > 0 else 0

    return [
        {
            "num": media_str,
            "label": "duração média por afastamento — a redução desse indicador é prioridade",
        },
        {
            "num": regional_label,
            "label": f"regional com maior incidência — {regional_count} eventos no período",
        },
        {
            "num": cid_combo,
            "label": f"juntos representam {cid_pct:.0f}% dos diagnósticos",
        },
    ]


def model_cities(df: pd.DataFrame, max_cities: int = 4) -> pd.DataFrame:
    """Cidades modelo: regionais com baixa incidência."""
    if df.empty:
        return pd.DataFrame(columns=["regional", "eventos", "dias", "media_dias"])
    agg = (
        df.groupby("regional")
        .agg(eventos=("data_inicio", "size"), dias=("dias", "sum"), media_dias=("dias", "mean"))
        .reset_index()
    )
    agg = agg[(agg["eventos"] <= 3) & (agg["regional"] != "Não informado")]
    return agg.sort_values("eventos").head(max_cities).reset_index(drop=True)
