---
name: fifine setup
description: Palavra-chave para gerar comandos Key down do OpenDeck para o Fifine AmpliGame D6 — aguardar nome do app para retornar o comando correto
type: feedback
---

Quando o usuário digitar **"fifine setup"**, aguardar ele informar o nome do programa/aplicação desejado, depois retornar o comando correto para o campo **Key down** no OpenDeck.

**Why:** O usuário usa o OpenDeck com o Fifine AmpliGame D6 para abrir apps via botões físicos. O campo Key down aceita comandos shell (ex: `flatpak run org.qbittorrent.qBittorrent`).

**How to apply:**
1. Aguardar o usuário informar o nome do app
2. Identificar se é Flatpak, binário nativo, script, ou Steam
3. Retornar apenas o comando limpo para colar no Key down

**Lógica para gerar o comando:**
- Flatpak: `flatpak run <app-id>` (ex: `flatpak run org.videolan.VLC`)
- Binário nativo no PATH: apenas o nome do binário (ex: `steam`, `obs`)
- Steam game: `steam steam://rungameid/<id>`
- Script: caminho absoluto (ex: `/home/linuxpc/scripts/meu_script.sh`)
- App com argumento: `flatpak run <id> --arg`

Para descobrir o app-id Flatpak correto, sugerir: `flatpak list --app | grep -i <nome>`
