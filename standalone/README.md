# Planilha Painel — versão HTML offline

Um único arquivo `.html` com a planilha embutida. Roda em qualquer navegador, **sem instalar Python** no PC de uso.

## Gerar o dashboard

```bat
cd standalone
python build.py
```

Marcas: `build-grafyco.bat` · `build-pronuxfin.bat` · ou `python build.py --brand grafyco|pronuxfin`

Usa `../data/planilha.csv` se existir; senão `../data/planilha.exemplo.csv`.

Saída: **`dashboard.html`**

## Usar

1. Copie `dashboard.html` para o PC (pendrive, rede, e-mail).
2. Duplo clique para abrir no Chrome ou Edge.
3. Para atualizar dados:
   - **Carregar planilha** — escolha um `.csv`
   - ou arraste o CSV na janela
4. **Salvar versão atualizada** — gera `{prefixo}-AAAAMMDD-HHMM-seunome.html` com dados embutidos (prefixo conforme a marca).

## Cenário típico

1. Abre `dashboard.html` (dados da última geração)
2. Arrasta o CSV novo do Excel
3. Confere KPIs e gráficos
4. Salva versão atualizada para compartilhar

## Requisitos

- Navegador moderno (Chrome, Edge, Firefox)
- Python **só na máquina que gera** o HTML (`build.py`), não no PC que só visualiza

## Personalizar textos

Edite `../profiles.py` (ou `PLANILHA_BRAND`) e rode `build.py` de novo.
