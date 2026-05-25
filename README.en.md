# Spreadsheet Dashboard

Interactive dashboard from **CSV/Excel** exports — KPIs, charts, and filters. Runs **offline** as a single HTML file, or locally with **Streamlit** for development.

The repository ships only **synthetic sample data** (`data/planilha.exemplo.csv`). Keep real spreadsheets on your machine (`data/planilha.csv` is gitignored).

## Two run modes

| Mode | Path | Best for |
|------|------|----------|
| **Offline HTML** | `standalone/dashboard.html` | Corporate PCs without Python |
| **Streamlit** | `app.py` + `run.bat` | Local development and QA |

Offline usage: [`standalone/README.md`](standalone/README.md)

## Quick start

### Offline HTML (recommended)

```bat
cd standalone
python build.py
```

Open `standalone/dashboard.html` in your browser.

### Streamlit

1. Python 3.10+
2. Run `run.bat` (creates `.venv` and installs dependencies)
3. Copy sample data if needed:

```bat
copy data\planilha.exemplo.csv data\planilha.csv
```

## Spreadsheet format

- Delimiter: `;` (semicolon)
- With or without header row (detects labels such as `CARGO ATUAL`, leave start date columns, etc.)
- Encoding: UTF-8 preferred

Main fields (any column order when a header row is present):

| Field | Accepted header labels |
|-------|------------------------|
| Start date | `( Inicio do afastamento )`, `INÍCIO DO AFASTAMENTO` |
| Days | `QUANTIDADE DE DIAS DE AFASTAMENTOS` |
| Role | `CARGO ATUAL` |
| ICD/CID | `CID 1`, `CID` |

Without a header: use the default 11-column layout (see `data/README.md`).

## Project layout

```
dashboard-planilha/
├── branding.py           # Active brand (from profiles.py)
├── profiles.py           # default | pronuxfin | grafyco
├── app.py                # Streamlit UI
├── data/
│   ├── planilha.exemplo.csv
│   └── planilha.csv        # local only (.gitignore)
├── standalone/
│   ├── template.html
│   └── build.py
└── src/
    ├── loader.py
    ├── charts.py
    └── styling.py
```

## Charts

- **HTML**: SVG gradients, moving average area, donut charts
- **Streamlit**: Plotly with shared theme (`src/chart_theme.py`)

## Publishing

Standalone GitHub repo — ready-made **About** description: [docs/REPOSITORY-DESCRIPTIONS.md](docs/REPOSITORY-DESCRIPTIONS.md) · steps: [GITHUB.md](GITHUB.md)

## Privacy

Do not commit spreadsheets with personal or health data. `.gitignore` excludes `data/planilha.csv` and generated `standalone/dashboard.html`.

## License

MIT — see [LICENSE](LICENSE).
