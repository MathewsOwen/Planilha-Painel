# Publicar no GitHub

Repositório **standalone** do Planilha Painel (projeto separado de PRONUXFIN e GRAFYCO).

## Antes do push

- [ ] `data/planilha.csv` **fora** do commit (`git status`)
- [ ] Apenas `data/planilha.exemplo.csv` versionado
- [ ] `standalone/dashboard.html` no `.gitignore` (gerar localmente)
- [ ] README, README.en.md e LICENSE incluídos

## Comandos

**Importante:** rode `git init` **dentro** da pasta `dashboard-planilha`, não na raiz do PronuxFin (evita subir backend, web, zips, etc.).

```bash
cd dashboard-planilha
git init
git add .
git commit -m "feat: Planilha Painel — dashboard CSV offline e Streamlit"
git branch -M main
git remote add origin https://github.com/SEU_USUARIO/planilha-painel.git
git push -u origin main
```

## Descrição do repositório

Textos prontos para colar no **About** do GitHub: [docs/REPOSITORY-DESCRIPTIONS.md](docs/REPOSITORY-DESCRIPTIONS.md)

**Resumo rápido**

| | |
|---|---|
| **PT** | Painel analítico a partir de CSV/Excel: HTML offline com KPIs, gráficos e filtros, ou Streamlit local. Só dados de exemplo no Git. |
| **EN** | CSV/Excel analytics dashboard: offline HTML with KPIs, charts and filters, or local Streamlit. Sample data only in the repo. |

**Topics:** `dashboard` `csv` `spreadsheet` `streamlit` `plotly` `data-visualization` `python` `offline` `analytics`
