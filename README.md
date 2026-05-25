# Planilha Painel

[![Painel online](https://img.shields.io/badge/painel-online-0a2c5b?style=for-the-badge)](https://mathewsowen.github.io/Planilha-Painel/)
[![Repo](https://img.shields.io/badge/GitHub-Planilha--Painel-24292f?style=for-the-badge)](https://github.com/MathewsOwen/Planilha-Painel)

**Painel online (dados fictícios):** https://mathewsowen.github.io/Planilha-Painel/

> Se o link ainda não abrir: **Settings → Pages → Deploy from a branch → `main` → `/docs`** (veja [docs/PAGES-SETUP.md](docs/PAGES-SETUP.md)).

Transforme exportações de **CSV/Excel** em um painel executivo — KPIs, gráficos e filtros. Funciona **100% offline** (um único HTML) ou com **Streamlit** para desenvolvimento local.

**English:** [README.en.md](README.en.md)

Não inclui dados reais de nenhuma empresa: use `data/planilha.exemplo.csv` no Git e mantenha `data/planilha.csv` apenas na sua máquina.

## Duas versões

| Versão | Caminho | Quando usar |
|--------|---------|-------------|
| **HTML offline** | `standalone/dashboard.html` | PC corporativo sem instalar Python |
| **Streamlit** | `app.py` + `run.bat` | Desenvolvimento e testes locais |

➡️ Uso offline: [`standalone/README.md`](standalone/README.md)

## Início rápido

### HTML (recomendado na empresa)

```bat
cd standalone
python build.py
```

Abra `standalone/dashboard.html` no navegador.

**Personalizar textos:** clique no botão **✏️** (canto inferior direito) para renomear filtros (ex.: Cargo → Estoque, Prateleira) e títulos dos blocos. Use **Salvar versão atualizada** para gravar no arquivo HTML.

**Trocar planilha:** ao carregar um CSV novo, aparece um alerta central lembrando que as colunas devem ser iguais às do modelo do painel.

### Streamlit

1. Python 3.10+
2. Duplo clique em `run.bat`
3. Coloque seus dados em `data/planilha.csv`:

```bat
copy data\planilha.exemplo.csv data\planilha.csv
```

## Planilha

- Separador: `;`
- Com ou sem linha de cabeçalho (detecta `CARGO ATUAL`, `INÍCIO DO AFASTAMENTO`, etc.)
- Encoding: UTF-8

Colunas principais (podem estar em qualquer ordem se houver cabeçalho):

| Campo | Nomes aceitos no cabeçalho |
|-------|----------------------------|
| Início | `( Inicio do afastamento )`, `INÍCIO DO AFASTAMENTO` |
| Dias | `QUANTIDADE DE DIAS DE AFASTAMENTOS` |
| Cargo | `CARGO ATUAL` |
| CID | `CID 1`, `CID` |

Sem cabeçalho: use a ordem padrão de 11 colunas (ver `data/README.md`).

## Estrutura

```
dashboard-planilha/
├── profiles.py           # Perfis de marca (padrão: Planilha Painel)
├── branding.py           # Perfil ativo (PLANILHA_BRAND)
├── app.py                # Streamlit
├── run.bat
├── data/
│   ├── planilha.exemplo.csv   # commitável (fictício)
│   └── planilha.csv           # local, no .gitignore
├── standalone/
│   ├── template.html
│   ├── build.py
│   └── dashboard.html         # gerado, no .gitignore
└── src/
    ├── loader.py
    ├── metrics.py
    ├── charts.py
    ├── chart_theme.py
    └── styling.py
```

## Gráficos

- **HTML offline**: SVG com gradientes, área sob a média móvel, donuts com sombra
- **Streamlit**: Plotly com paleta em gradiente, hover unificado, export PNG

Tema: `src/chart_theme.py` · estilos: `src/styling.py`

## Personalização

Edite `profiles.py` (nome, cores, prefixo do arquivo). Perfil padrão: **Planilha Painel**.

## Publicar no GitHub

Repositório standalone — descrição pronta para o **About**: [docs/REPOSITORY-DESCRIPTIONS.md](docs/REPOSITORY-DESCRIPTIONS.md) · passo a passo: [GITHUB.md](GITHUB.md)

## Privacidade

Não faça commit de planilhas com dados pessoais ou de saúde. O `.gitignore` ignora `data/planilha.csv`.
