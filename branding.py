"""Identidade visual e textos do painel.

Perfil ativo: variável de ambiente PLANILHA_BRAND ou argumento --brand no build.
Valores: default | pronuxfin | grafyco
"""

from __future__ import annotations

import os

from profiles import CSV_EXAMPLE, CSV_LOCAL, DATA_DIR, PROFILES, VALID_PROFILES


def active_profile_name() -> str:
    name = (os.environ.get("PLANILHA_BRAND") or "default").strip().lower()
    return name if name in PROFILES else "default"


def load_profile(name: str | None = None) -> dict:
    key = (name or active_profile_name()).strip().lower()
    if key not in PROFILES:
        key = "default"
    return PROFILES[key]


_p = load_profile()

APP_NAME = _p["APP_NAME"]
APP_TITLE = _p["APP_TITLE"]
APP_HEADLINE = _p["APP_HEADLINE"]
APP_SUBTITLE = _p["APP_SUBTITLE"]
APP_FOOTER = _p["APP_FOOTER"]
APP_FILE_PREFIX = _p["APP_FILE_PREFIX"]
THEME = _p["THEME"]
