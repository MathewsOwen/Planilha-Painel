# Publicar o painel online (GitHub Pages)

## Erro comum

Se aparecer falha em **configure-pages** ou **deploy-pages**, o repositório ainda não estava com Pages ligado para **GitHub Actions**. Este projeto usa o modo mais simples: pasta **`/docs`**.

## Configuração (uma vez)

1. Abra o repositório no GitHub → **Settings** → **Pages**
2. Em **Build and deployment** → **Source**, escolha **Deploy from a branch**
3. **Branch:** `main` · **Folder:** `/docs`
4. Salve e aguarde 1–2 minutos

URL do painel: **https://mathewsowen.github.io/Planilha-Painel/**

O arquivo servido é `docs/index.html` (dados fictícios de `planilha.exemplo.csv`).

## Atualização automática

A cada push em `main`, o workflow **Atualizar painel publicado** regera `docs/index.html` e faz commit, se houver mudança no template ou na planilha de exemplo.
