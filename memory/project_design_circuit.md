---
name: Design Circuit Player
description: App local tipo Hotmart para assistir o curso Design Circuit, com tracking de progresso e player externo Haruna
type: project
---

Player local para o curso Design Circuit.

**Why:** Curso baixado localmente em pastas, precisava de interface com tracking de progresso estilo Hotmart.

**How to apply:** Ao falar sobre este projeto, considerar a arquitetura atual e os problemas já resolvidos.

## Localização dos arquivos

- **Curso:** `/var/home/linuxpc/Linux_Storage/Media/Videos/Cursos/Design Circuit/`
- **App:** `~/.local/share/course-player/` (app.py + templates/index.html)
- **Progresso salvo:** `~/.local/share/course-player/progress.json`
- **Atalho desktop:** `~/.local/share/applications/design-circuit.desktop`
- **Ícone:** `~/.local/share/course-player/icon.svg`

## Estrutura do curso

- 13 seções (pastas numeradas), 180+ aulas
- Estrutura: `Seção/Aula/video.mp4` + `descricao.html`/`links.html` + `00. Materiais/`

## Stack

- Python + Flask (`pip install flask --user`)
- Interface web servida em `http://127.0.0.1:5000`
- Inicia via `~/.local/share/course-player/start.sh` (ou pelo launcher do KDE)

## Decisões de arquitetura

- **Player externo:** Firefox Flatpak não decodifica H.264 via `<video>` nativa → vídeos abrem no **Haruna** (`flatpak run org.kde.haruna`) via endpoint `/api/play`
- **Auto-mark:** quando Haruna fecha, aula é marcada como vista automaticamente (subprocess.run blocks até fechar)
- **Ordenação:** natural sort numérico (`natural_key`) para evitar 10,11,12 antes de 2,3,4
- **Range requests:** implementado manualmente no Flask para streaming correto (necessário mesmo que o player seja externo, caso mude no futuro)

## Como iniciar

```bash
~/.local/share/course-player/start.sh
# ou pelo launcher do KDE buscando "Design Circuit"
```

Se já estiver rodando, o script apenas abre o browser. Logs em `/tmp/design-circuit.log`.
