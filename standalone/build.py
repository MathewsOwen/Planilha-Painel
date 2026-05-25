"""Gera o dashboard HTML standalone com a planilha embutida.

Uso:
    python build.py [--brand default|pronuxfin|grafyco] [caminho/para/planilha.csv]

Se nenhum caminho for passado, usa ../data/planilha.exemplo.csv (ou planilha.csv se existir)

Saída: dashboard.html (na mesma pasta)

Aceita dois formatos de planilha:
1. Sem cabeçalho, 11 colunas (formato original)
2. Com linhas vazias no topo + cabeçalho contendo "CARGO ATUAL" +
   colunas extras à direita (formato planilha 2). Será limpo automaticamente.
"""

from __future__ import annotations

import re
import sys
import unicodedata
from datetime import datetime
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
from profiles import CSV_EXAMPLE, CSV_LOCAL, PROFILES, VALID_PROFILES  # noqa: E402

# Campos internos → nomes possíveis no cabeçalho do Excel/OneDrive (qualquer posição)
COLUMN_ALIASES: dict[str, list[str]] = {
    "cargo_ocupado": ["CARGO ATUAL"],
    "cargo_origem": ["CARGO DE ORIGEM"],
    "lotacao": ["AREA DE EXERCICIO", "ÁREA DE EXERCÍCIO"],
    "setor": ["LOTACAO II", "LOTAÇÃO II"],
    "superintendencia": ["LOTACAO III", "LOTAÇÃO III"],
    "data_inicio": [
        "( INICIO DO AFASTAMENTO )",
        "( INÍCIO DO AFASTAMENTO )",
        "INICIO DO AFASTAMENTO",
        "INÍCIO DO AFASTAMENTO",
    ],
    "dias": [
        "QUANTIDADE DE DIAS DE AFASTAMENTOS",
        "QUANTIDADE DE DIAS DE AFASTAMENTO",
        "QUANTIDADE DE DIAS",
    ],
    "data_fim": [
        "DATA PREVISTA PARA O RETORNO",
        "DATA PREVISTA PARA RETORNO",
        "DATA DE RETORNO",
        "DATA FIM",
    ],
    "cid_raw": ["CID 1", "CID1", "CID 10", "CID", "COD CID", "CÓD CID", "CODIGO CID"],
    "idade": ["IDADE"],
}

# Ordem fixa do CSV normalizado (sem cabeçalho) — usada pelo dashboard
OUTPUT_FIELDS = [
    "cargo_ocupado",
    "cargo_origem",
    "lotacao",
    "setor",
    "superintendencia",
    "data_inicio",
    "dias",
    "data_fim",
    "cid_raw",
    "_genero_ignorado",
    "idade",
]


def _strip_accents(text: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFKD", text) if not unicodedata.combining(c)
    )


def _norm_header(text: str) -> str:
    s = _strip_accents(str(text or "")).upper()
    s = re.sub(r"[°ºª()\[\]]", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _is_inicio_afastamento_column(cell_norm: str) -> bool:
    if not cell_norm:
        return False
    if "QUANTIDADE" in cell_norm and "DIAS" in cell_norm:
        return False
    if "RETORNO" in cell_norm or "PREVISTA" in cell_norm:
        return False
    return ("INICIO" in cell_norm or "INIC" in cell_norm) and (
        "AFASTAMENTO" in cell_norm or "AFAST" in cell_norm
    )


def _find_inicio_column_index(norms: list[str], used: set[int] | None = None) -> int | None:
    for i, hn in enumerate(norms):
        if used and i in used:
            continue
        if _is_inicio_afastamento_column(hn):
            return i
    return None


def _header_matches(cell_norm: str, alias_norm: str, field: str) -> bool:
    if not cell_norm or not alias_norm:
        return False
    if field == "data_fim" and _is_inicio_afastamento_column(cell_norm):
        return False
    if field == "data_inicio" and _is_inicio_afastamento_column(cell_norm):
        return True
    if cell_norm == alias_norm:
        return True
    if alias_norm.startswith("CID") or field == "cid_raw":
        return cell_norm == alias_norm or cell_norm.startswith(alias_norm + " ")
    if field == "data_inicio":
        return _is_inicio_afastamento_column(cell_norm) or alias_norm in cell_norm
    if field == "dias":
        return "QUANTIDADE" in cell_norm and "DIAS" in cell_norm
    if field == "data_fim":
        return (
            "RETORNO" in cell_norm
            or "PREVISTA" in cell_norm
            or alias_norm in cell_norm
        )
    return alias_norm in cell_norm or cell_norm in alias_norm


def find_column_map(header_cells: list[str]) -> dict[str, int]:
    """Mapeia nome do campo → índice da coluna no CSV (qualquer posição)."""
    norms = [_norm_header(c) for c in header_cells]
    col_map: dict[str, int] = {}
    used: set[int] = set()
    for field, aliases in COLUMN_ALIASES.items():
        for alias in aliases:
            an = _norm_header(alias)
            for i, hn in enumerate(norms):
                if i in used:
                    continue
                if _header_matches(hn, an, field):
                    col_map[field] = i
                    used.add(i)
                    break
            if field in col_map:
                break
    ini_idx = _find_inicio_column_index(norms, used)
    if ini_idx is not None:
        col_map["data_inicio"] = ini_idx
        used.add(ini_idx)
    return col_map


def _is_header_row(cells: list[str]) -> bool:
    norms = [_norm_header(c) for c in cells]
    hits = 0
    for field, aliases in COLUMN_ALIASES.items():
        for alias in aliases:
            an = _norm_header(alias)
            if any(_header_matches(hn, an, field) for hn in norms if hn):
                hits += 1
                break
    return hits >= 3


def _is_title_row(cells: list[str]) -> bool:
    return any(c and "MAPEAMENTO" in c.upper() for c in cells)


def _row_from_map(cells: list[str], col_map: dict[str, int]) -> list[str]:
    def get(field: str) -> str:
        idx = col_map.get(field)
        if idx is None or idx >= len(cells):
            return ""
        return cells[idx].strip()

    return [
        get("cargo_ocupado"),
        get("cargo_origem"),
        get("lotacao"),
        get("setor"),
        get("superintendencia"),
        get("data_inicio"),
        get("dias"),
        get("data_fim"),
        get("cid_raw"),
        "",  # gênero — nunca exportado pro dashboard
        get("idade"),
    ]


def _detect_delimiter(lines: list[str]) -> str:
    sample = [ln for ln in lines if ln.strip()][:40]
    if not sample:
        return ";"
    scores = {";": 0, ",": 0, "\t": 0}
    for line in sample:
        in_quote = False
        for ch in line:
            if ch == '"':
                in_quote = not in_quote
                continue
            if not in_quote and ch in scores:
                scores[ch] += 1
    best = max(scores.items(), key=lambda x: x[1])
    return best[0] if best[1] > 0 else ";"


def _clean_cell(s: str) -> str:
    return (
        str(s or "")
        .replace("\ufeff", "")
        .replace("\u00a0", " ")
        .strip()
    )


def normalize_csv(csv_text: str) -> str:
    """Normaliza planilha: localiza colunas PELO NOME do cabeçalho (não pela posição).

    - Ignora colunas extras (SEXO, etc.) que não estão na lista
    - Funciona se as colunas certas estiverem no meio ou no fim da planilha
    - Detecta separador ; , ou tab (exportações diferentes do Excel)
    - Saída: CSV sem cabeçalho, 11 colunas na ordem interna fixa
    """
    lines = csv_text.splitlines()
    delim = _detect_delimiter(lines)
    parsed: list[list[str]] = []
    for raw in lines:
        if not raw.strip():
            continue
        cells = [_clean_cell(c) for c in raw.split(delim)]
        if not any(cells):
            continue
        parsed.append(cells)

    # Acha linha de cabeçalho
    header_idx = None
    col_map: dict[str, int] = {}
    for i, cells in enumerate(parsed):
        if _is_title_row(cells):
            continue
        if _is_header_row(cells):
            header_idx = i
            col_map = find_column_map(cells)
            break

    out_rows: list[str] = []
    skipped_blank = 0
    skipped_invalid = 0
    used_header_map = bool(col_map)

    # Campos mínimos para considerar linha válida
    required = {"cargo_ocupado", "data_inicio"}

    start_idx = (header_idx + 1) if header_idx is not None else 0

    for i, cells in enumerate(parsed):
        if header_idx is not None and i <= header_idx:
            if i != header_idx:
                skipped_blank += 1
            continue
        if _is_title_row(cells):
            skipped_blank += 1
            continue
        if i == header_idx:
            continue
        if _is_header_row(cells):
            skipped_blank += 1
            continue

        if col_map:
            row = _row_from_map(cells, col_map)
        else:
            # Fallback: planilha antiga sem cabeçalho (11 colunas na ordem fixa)
            cells11 = cells[:11]
            while len(cells11) < 11:
                cells11.append("")
            row = cells11

        if not row[0]:
            skipped_invalid += 1
            continue
        date_cell = row[5].replace("\u00a0", " ").strip()
        if not date_cell or "/" not in date_cell and "-" not in date_cell:
            skipped_invalid += 1
            continue

        out_rows.append(";".join(row))

    if used_header_map:
        found = [f for f in COLUMN_ALIASES if f in col_map]
        missing = [f for f in COLUMN_ALIASES if f not in col_map and f != "idade" and f != "data_fim"]
        print(f"[INFO] Colunas localizadas pelo nome: {', '.join(found)}")
        if missing:
            print(f"[INFO] Colunas opcionais não encontradas: {', '.join(missing)}")
    else:
        print("[INFO] Sem cabeçalho reconhecido — usando ordem fixa das 11 primeiras colunas")

    if skipped_blank > 0:
        print(f"[INFO] {skipped_blank} linha(s) em branco / título descartada(s)")
    if skipped_invalid > 0:
        print(f"[INFO] {skipped_invalid} linha(s) sem dados válidos descartada(s)")
    print(f"[INFO] Linhas válidas preservadas: {len(out_rows)}")

    return "\n".join(out_rows) + "\n"


def _parse_args(argv: list[str]) -> tuple[str, Path | None]:
    brand = "default"
    csv_override: Path | None = None
    args = list(argv)
    i = 0
    while i < len(args):
        a = args[i]
        if a in ("--brand", "-b") and i + 1 < len(args):
            brand = args[i + 1].strip().lower()
            i += 2
            continue
        if not a.startswith("-") and csv_override is None:
            csv_override = Path(a)
        i += 1
    if brand not in PROFILES:
        print(f"[ERRO] Perfil inválido: {brand}. Use: {', '.join(VALID_PROFILES)}")
        sys.exit(1)
    return brand, csv_override


def main():
    here = Path(__file__).parent
    brand, csv_arg = _parse_args(sys.argv[1:])
    profile = PROFILES[brand]

    data_dir = here.parent / "data"
    default_csv = data_dir / CSV_LOCAL
    if not default_csv.exists():
        default_csv = data_dir / CSV_EXAMPLE
    csv_path = csv_arg if csv_arg is not None else default_csv
    template = here / "template.html"
    output = here / "dashboard.html"

    if not csv_path.exists():
        print(f"[ERRO] Planilha não encontrada: {csv_path}")
        sys.exit(1)
    if not template.exists():
        print(f"[ERRO] Template não encontrado: {template}")
        sys.exit(1)

    # Lê o CSV preservando o conteúdo bruto. Tenta utf-8-sig primeiro pra remover BOM.
    csv_text = None
    for enc in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
        try:
            csv_text = csv_path.read_text(encoding=enc)
            print(f"[OK] CSV lido em {enc}")
            break
        except UnicodeDecodeError:
            continue
    if csv_text is None:
        print("[ERRO] Falha ao decodificar o CSV.")
        sys.exit(1)

    # Normaliza
    csv_text = normalize_csv(csv_text)

    # Escapa backticks e ${} para template literal JS
    csv_escaped = (
        csv_text.replace("\\", "\\\\")
        .replace("`", "\\`")
        .replace("${", "\\${")
    )

    template_html = template.read_text(encoding="utf-8")
    generated_at = datetime.now().strftime("%d/%m/%Y %H:%M")

    # Autor inicial e histórico inicial (vazio até alguém atualizar pela primeira vez)
    initial_author = "Importação inicial"
    initial_history = "[]"
    theme = profile["THEME"]

    final = (
        template_html
        .replace("__CSV_DATA__", csv_escaped)
        .replace("__GENERATED_AT__", generated_at)
        .replace("__UPDATED_BY__", initial_author)
        .replace("__UPDATE_HISTORY__", initial_history)
        .replace("__APP_TITLE__", profile["APP_TITLE"])
        .replace("__APP_HEADLINE__", profile["APP_HEADLINE"])
        .replace("__APP_SUBTITLE__", profile["APP_SUBTITLE"])
        .replace("__APP_FOOTER__", profile["APP_FOOTER"])
        .replace("__APP_FILE_PREFIX__", profile["APP_FILE_PREFIX"])
        .replace("__UI_LABELS__", "{}")
        .replace("__CSV_COLUMNS__", "{}")
        .replace("__CSV_OPTIONS__", '{"delimiter":";"}')
        .replace("__APP_THEME__", '"light"')
        .replace("__THEME_BLUE__", theme["blue"])
        .replace("__THEME_BLUE_DARK__", theme["blue_dark"])
        .replace("__THEME_BLUE_MEDIUM__", theme["blue_medium"])
        .replace("__THEME_BLUE_LIGHT__", theme["blue_light"])
        .replace("__THEME_BLUE_ACCENT__", theme["blue_accent"])
        .replace("__THEME_YELLOW__", theme["yellow"])
        .replace("__THEME_TEXT_PRIMARY__", theme["text_primary"])
    )

    output.write_text(final, encoding="utf-8")

    size_kb = output.stat().st_size / 1024
    print(f"[OK] Perfil: {brand}")
    print(f"[OK] Dashboard gerado: {output}")
    print(f"     Tamanho: {size_kb:.1f} KB")
    print(f"     Linhas no CSV: {len([l for l in csv_text.splitlines() if l.strip()])}")
    print(f"     Gerado em: {generated_at}")
    print()
    print("Para abrir, basta dar duplo clique no arquivo .html")


if __name__ == "__main__":
    main()
