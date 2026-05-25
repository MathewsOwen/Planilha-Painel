# Publicar no GitHub (repositório standalone)

Este projeto sobe como **repositório próprio** no GitHub (ex.: `planilha-painel`). Não é o monorepo PRONUXFIN nem o GRAFYCO Platform.

## Checklist

- [ ] `git status` sem `data/planilha.csv`
- [ ] Sem `standalone/dashboard.html` no commit
- [ ] Descrição do About copiada de [REPOSITORY-DESCRIPTIONS.md](REPOSITORY-DESCRIPTIONS.md)
- [ ] Topics adicionados no GitHub

## Gerar o HTML antes de usar (local)

```bat
cd standalone
python build.py
```

O arquivo gerado fica fora do Git (`.gitignore`).

## Perfis de marca (opcional, uso interno)

Se quiser testar visual PRONUXFIN ou GRAFYCO localmente: `build-pronuxfin.bat` / `build-grafyco.bat`. O repositório público usa o perfil neutro **Planilha Painel** (`python build.py`).
