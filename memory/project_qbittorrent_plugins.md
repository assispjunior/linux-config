---
name: qBittorrent plugins
description: Instalação em massa de 53 plugins de busca no qBittorrent via script
type: project
---

53 plugins públicos e não-pornográficos instalados no qBittorrent Flatpak.

**Why:** Usuário não conseguia instalar plugins .py pois o browser salvava como .txt.

**How to apply:** Quando usuário mencionar qBittorrent plugins, busca, engines.

## Detalhes
- qBittorrent: Flatpak `org.qbittorrent.qBittorrent` v5.1.4
- Pasta dos plugins: `~/.var/app/org.qbittorrent.qBittorrent/data/qBittorrent/nova3/engines/`
- Plugins instalados: 53 (públicos, sem conteúdo exclusivamente pornográfico)
- Excluídos: mypornclub, xxxclubto, sukebeisi, sukebei, pantsu, traht + todos os de sites privados

## Problema encontrado
`tokyotoshokan.py` causava `AttributeError: no attribute 'name'` que impedia o qBittorrent de abrir. Foi removido.
