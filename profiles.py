"""Perfis de marca para publicação (neutro, GRAFYCO, PRONUXFIN)."""

from __future__ import annotations

from typing import TypedDict


class Theme(TypedDict):
    blue: str
    blue_dark: str
    blue_medium: str
    blue_light: str
    blue_accent: str
    yellow: str
    text_primary: str


class BrandProfile(TypedDict):
    APP_NAME: str
    APP_TITLE: str
    APP_HEADLINE: str
    APP_SUBTITLE: str
    APP_FOOTER: str
    APP_FILE_PREFIX: str
    THEME: Theme


DATA_DIR = "data"
CSV_LOCAL = "planilha.csv"
CSV_EXAMPLE = "planilha.exemplo.csv"

_THEME_PRONUX: Theme = {
    "blue": "#0a2c5b",
    "blue_dark": "#06204a",
    "blue_medium": "#1d4f91",
    "blue_light": "#4a7cc1",
    "blue_accent": "#3b82f6",
    "yellow": "#f4b942",
    "text_primary": "#0a2c5b",
}

PROFILES: dict[str, BrandProfile] = {
    "default": {
        "APP_NAME": "Planilha Painel",
        "APP_TITLE": "Planilha Painel · Análise de dados",
        "APP_HEADLINE": "Painel de análise<br>de planilha",
        "APP_SUBTITLE": "Indicadores, categorias e evolução a partir do seu CSV",
        "APP_FOOTER": "Planilha Painel",
        "APP_FILE_PREFIX": "planilha-painel",
        "THEME": dict(_THEME_PRONUX),
    },
    "pronuxfin": {
        "APP_NAME": "PRONUXFIN Sheets",
        "APP_TITLE": "PRONUXFIN Sheets · Data analysis",
        "APP_HEADLINE": "Spreadsheet analytics<br>dashboard",
        "APP_SUBTITLE": "KPIs, categories and trends from your CSV export",
        "APP_FOOTER": "PRONUXFIN",
        "APP_FILE_PREFIX": "pronuxfin-sheets",
        "THEME": dict(_THEME_PRONUX),
    },
    "grafyco": {
        "APP_NAME": "GRAFYCO Insights",
        "APP_TITLE": "GRAFYCO Insights · Data analysis",
        "APP_HEADLINE": "Operational insights<br>from your spreadsheet",
        "APP_SUBTITLE": "KPIs, categories and time series — offline-ready HTML",
        "APP_FOOTER": "GRAFYCO",
        "APP_FILE_PREFIX": "grafyco-insights",
        "THEME": {
            "blue": "#0a1628",
            "blue_dark": "#060d1a",
            "blue_medium": "#2563b8",
            "blue_light": "#5eb8ff",
            "blue_accent": "#f5b942",
            "yellow": "#f5b942",
            "text_primary": "#0a1628",
        },
    },
}

VALID_PROFILES = tuple(PROFILES.keys())
