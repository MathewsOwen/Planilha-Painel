"""Leitura e normalização da planilha CSV (afastamentos, RH, indicadores por CID)."""

from __future__ import annotations

import os
import re
import unicodedata
from pathlib import Path
from typing import Optional

import pandas as pd

COLUMNS = [
    "cargo_ocupado",
    "cargo_origem",
    "lotacao",
    "setor",
    "superintendencia",
    "data_inicio",
    "dias",
    "data_fim",
    "cid_raw",
    "genero_ignorado",
    "idade",
]

CID_BLOCKS = {
    "F00-F09": "Transtornos mentais orgânicos",
    "F10-F19": "Uso de substâncias psicoativas",
    "F20-F29": "Esquizofrenia e psicoses",
    "F30-F39": "Transtornos do humor",
    "F40-F49": "Transtornos neuróticos / estresse",
    "F50-F59": "Síndromes comportamentais",
    "F60-F69": "Transtornos da personalidade",
    "F70-F79": "Retardo mental",
    "F80-F89": "Transtornos do desenvolvimento",
    "F90-F98": "Transtornos comportamentais (infância)",
    "F99":     "Transtorno mental não especificado",
}

CID_NAMES = {
    "F00": "Demência na doença de Alzheimer",
    "F03": "Demência não especificada",
    "F05": "Delirium",
    "F10": "Transtornos por uso de álcool",
    "F11": "Transtornos por uso de opioides",
    "F12": "Transtornos por uso de canabinoides",
    "F17": "Transtornos por uso de tabaco",
    "F19": "Múltiplas drogas e psicoativas",
    "F20": "Esquizofrenia",
    "F25": "Transtornos esquizoafetivos",
    "F29": "Psicose não orgânica não especificada",
    "F30": "Episódio maníaco",
    "F31": "Transtorno afetivo bipolar",
    "F32": "Episódio depressivo",
    "F33": "Transtorno depressivo recorrente",
    "F34": "Transtornos persistentes do humor",
    "F38": "Outros transtornos do humor",
    "F39": "Transtorno do humor não especificado",
    "F40": "Transtornos fóbico-ansiosos",
    "F41": "Outros transtornos ansiosos",
    "F42": "Transtorno obsessivo-compulsivo",
    "F43": "Reações ao estresse e adaptação",
    "F44": "Transtornos dissociativos",
    "F45": "Transtornos somatoformes",
    "F48": "Outros transtornos neuróticos",
    "F50": "Transtornos da alimentação",
    "F51": "Transtornos não orgânicos do sono",
    "F52": "Disfunção sexual",
    "F60": "Transtornos específicos da personalidade",
    "F63": "Transtornos dos hábitos e impulsos",
    "F70": "Retardo mental leve",
    "F90": "Transtornos hipercinéticos",
    "F99": "Transtorno mental não especificado",
}


def _strip_accents(text: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFKD", text) if not unicodedata.combining(c)
    )


def _clean_str(value) -> Optional[str]:
    if pd.isna(value):
        return None
    s = str(value).strip()
    if not s or s.upper() in {"#N/D", "N/A", "NA", "-", "—"}:
        return None
    s = re.sub(r"\s+", " ", s)
    return s


def _normalize_regional(value) -> str:
    if value is None or pd.isna(value) or not str(value).strip():
        return "Não informado"
    s = str(value).upper()
    s = re.sub(r"^SUPERINTEND[EÊ]NCIA\s+(DE|EM|DO|DA)\s+", "", s)
    s = re.sub(r"\s*-\s*SUPERINTEND[EÊ]NCIA\s*$", "", s)
    s = s.replace("(SEDE)", "SEDE").strip()
    s = re.sub(r"\s+", " ", s).strip(" -")
    if not s:
        return "Não informado"
    return s.title().replace("Sp", "SP")


def _normalize_cargo(value) -> str:
    if value is None or pd.isna(value) or not str(value).strip():
        return "Não informado"
    flat = _strip_accents(str(value)).upper().strip()
    if "OFICIAL ADMINISTRATIVO" in flat or "OFICIAL  ADMINISTRATIVO" in flat:
        return "Oficial Administrativo"
    if "AGENTE" in flat and "TRANSITO" in flat:
        return "Agente de Operações"
    if "OFICIAL" in flat and "TRANSITO" in flat:
        return "Oficial de Operações"
    if "CCESP" in flat or "FCESP" in flat or "CONFIAN" in flat or "CHEFE" in flat or "ASSESSORIA" in flat:
        return "Cargo de Confiança"
    if "ASSISTENTE" in flat:
        return "Assistente Técnico"
    return str(value).title()


def _cid_group(cid_raw) -> Optional[str]:
    if cid_raw is None or pd.isna(cid_raw) or not str(cid_raw).strip():
        return None
    m = re.search(r"F\s*\.?\s*(\d{2,3})", str(cid_raw).upper().replace(" ", ""))
    if not m:
        return None
    digits = m.group(1)
    return f"F{digits[:2]}"


def _cid_block(group) -> Optional[str]:
    if group is None or pd.isna(group) or not str(group).strip():
        return None
    try:
        num = int(group[1:])
    except ValueError:
        return None
    if 0 <= num <= 9:
        return "F00-F09"
    if 10 <= num <= 19:
        return "F10-F19"
    if 20 <= num <= 29:
        return "F20-F29"
    if 30 <= num <= 39:
        return "F30-F39"
    if 40 <= num <= 49:
        return "F40-F49"
    if 50 <= num <= 59:
        return "F50-F59"
    if 60 <= num <= 69:
        return "F60-F69"
    if 70 <= num <= 79:
        return "F70-F79"
    if 80 <= num <= 89:
        return "F80-F89"
    if 90 <= num <= 98:
        return "F90-F98"
    if num == 99:
        return "F99"
    return None


def _age_bracket(age) -> str:
    if pd.isna(age):
        return "Não informado"
    a = int(age)
    if a <= 30:
        return "Até 30"
    if a <= 40:
        return "31–40"
    if a <= 50:
        return "41–50"
    if a <= 60:
        return "51–60"
    return "60+"


def _duration_bracket(d) -> str:
    if pd.isna(d):
        return "Não informado"
    d = int(d)
    if d <= 15:
        return "Curto (1–15d)"
    if d <= 60:
        return "Médio (16–60d)"
    if d <= 180:
        return "Longo (61–180d)"
    return "Muito longo (>180d)"


def _parse_date(value):
    if pd.isna(value):
        return pd.NaT
    s = str(value).strip()
    if not s:
        return pd.NaT
    for fmt in ("%d/%m/%Y", "%d/%m/%y", "%Y-%m-%d"):
        try:
            return pd.to_datetime(s, format=fmt)
        except (ValueError, TypeError):
            continue
    return pd.to_datetime(s, dayfirst=True, errors="coerce")


def load_data(csv_path: str | Path) -> pd.DataFrame:
    """Lê o CSV bruto e devolve DataFrame normalizado.

    Coluna 'genero' é removida intencionalmente conforme requisito.
    """
    csv_path = Path(csv_path)
    if not csv_path.exists():
        raise FileNotFoundError(f"Planilha não encontrada: {csv_path}")

    df = None
    last_err: Exception | None = None
    for enc in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
        try:
            df = pd.read_csv(
                csv_path,
                sep=";",
                header=None,
                names=COLUMNS,
                dtype=str,
                encoding=enc,
                skip_blank_lines=True,
                on_bad_lines="skip",
            )
            break
        except (UnicodeDecodeError, UnicodeError) as e:
            last_err = e
            continue
    if df is None:
        raise RuntimeError(f"Não foi possível ler {csv_path}: {last_err}")

    df = df.dropna(how="all").drop(columns=["genero_ignorado"])

    for col in ["cargo_ocupado", "cargo_origem", "lotacao", "setor", "superintendencia", "cid_raw"]:
        df[col] = df[col].map(_clean_str)

    df["data_inicio"] = df["data_inicio"].map(_parse_date)
    df["data_fim"] = df["data_fim"].map(_parse_date)
    df["dias"] = pd.to_numeric(df["dias"], errors="coerce")
    df["idade"] = pd.to_numeric(df["idade"], errors="coerce")

    df = df.dropna(subset=["data_inicio"]).reset_index(drop=True)

    df["regional"] = df["superintendencia"].map(_normalize_regional)
    df["cargo"] = df["cargo_ocupado"].map(_normalize_cargo)

    df["cid_group"] = df["cid_raw"].map(_cid_group)
    df["cid_block"] = df["cid_group"].map(_cid_block)
    df["cid_block_name"] = df["cid_block"].map(CID_BLOCKS)
    df["cid_name"] = df["cid_group"].map(lambda g: CID_NAMES.get(g, "Outros / Não classificado"))

    df["faixa_etaria"] = df["idade"].map(_age_bracket)
    df["duracao_categoria"] = df["dias"].map(_duration_bracket)

    df["ano"] = df["data_inicio"].dt.year
    df["mes"] = df["data_inicio"].dt.to_period("M").astype(str)
    df["mes_label"] = df["data_inicio"].apply(_format_mes_pt)
    df["ano_mes"] = df["data_inicio"].dt.to_period("M")

    return df


MESES_PT = {
    1: "Jan", 2: "Fev", 3: "Mar", 4: "Abr", 5: "Mai", 6: "Jun",
    7: "Jul", 8: "Ago", 9: "Set", 10: "Out", 11: "Nov", 12: "Dez",
}


def _format_mes_pt(dt) -> str:
    if pd.isna(dt):
        return ""
    return f"{MESES_PT[dt.month]}/{str(dt.year)[-2:]}"


def get_file_mtime(csv_path: str | Path) -> float:
    """Modification time do arquivo — usado como cache key."""
    return os.path.getmtime(csv_path)
