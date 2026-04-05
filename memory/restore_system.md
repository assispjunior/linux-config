---
name: System Restore Script
description: Script de restauração completo do sistema Bazzite — localização, conteúdo e como usar
type: project
---

Script de restauração do sistema em `~/.claude/restore/resgate.sh`.

**Why:** Para recuperar todo o setup do Bazzite após reinstalação com o mínimo de trabalho manual.

**How to apply:** Quando o usuário digitar "restore", o hook executa o script automaticamente. Se precisar atualizar o script após mudanças no sistema, recriar com base na memória atual.

## O que o script restaura (automaticamente)

1. **Flatpaks:** Firefox, qBittorrent, Heroic, Steam, Plex Desktop
2. **Firefox VA-API:** flatpak override com radeonsi + DRI para RX 9060 XT
3. **Firefox user.js:** startup page (rewards.bing.com) + media settings RDNA 4
4. **Tampermonkey userscript:** salvo em `~/.local/share/bing_rewards_session/bing_rewards.user.js`
5. **nvm + Node 20:** instalação e configuração no .bashrc
6. **Forge app:** recria o projeto Expo ou reinstala dependências
7. **Gaming:** gamemode group, sysctl 99-gaming.conf, NVMe scheduler udev rule, gamemode.ini
8. **Plex:** container systemd em `~/.config/containers/systemd/plex.container`

## O que exige ação manual após o script

- Tampermonkey: instalar extensão + importar userscript
- qBittorrent: baixar plugins manualmente (NÃO instalar tokyotoshokan.py)
- Plex: adicionar PLEX_CLAIM token + `systemctl --user start plex`
- Steam: launch options `gamemoderun mangohud %command%` por jogo
- Heroic: ativar MangoHud e GameMode nas configurações
- Eden: `async_presentation=true` em `~/.config/eden/qt-config.ini`
- Reboot após tudo para aplicar grupo gamemode + udev rules

## Fluxo após reinstalar Bazzite

```bash
# 1. Instalar Claude Code
curl -fsSL https://claude.ai/install.sh | sh

# 2. Digitar "restore" no Claude → script executa automaticamente

# 3. Fazer os passos manuais listados acima

# 4. Reboot
```

## Localização do script
`~/.claude/restore/resgate.sh`
