---
name: Reinstall Qbit
description: Restaurar os 52 plugins de busca do qBittorrent Flatpak após reinstalação
type: project
---

qBittorrent Flatpak `org.qbittorrent.qBittorrent` v5.1.4 com 52 plugins instalados.

## Pasta dos plugins
```
~/.var/app/org.qbittorrent.qBittorrent/data/qBittorrent/nova3/engines/
```

## Como reinstalar
```bash
cd ~/.var/app/org.qbittorrent.qBittorrent/data/qBittorrent/nova3/engines/
BASE="https://raw.githubusercontent.com/qbittorrent/search-plugins/master/nova3/engines"
for plugin in academictorrents acgrip ali213 anidex animetosho audiobookbay bitsearch bt4gprx btdig calidadtorrent cloudtorrents cpasbien darklibria divxtotal dmhy dodi_repacks dontorrent elitetorrent esmeraldatorrent fitgirl_repacks glotorrents kickasstorrents linuxtracker magnetdl maxitorrent mejortorrent mikan naranjatorrent nyaa nyaasi onlinefix pediatorrent pirateiro rockbox rutor sktorrent smallgames snowfl solidtorrents subsplease thepiratebay therarbg tomadivx torrent9 torrentdownload torrentdownloads torrentgalaxy uniondht yggtracker yourbittorrent yts zooqle; do
  curl -sL "$BASE/$plugin.py" -o "$plugin.py" 2>/dev/null || \
  curl -sL "https://raw.githubusercontent.com/v1k45/qbittorrent-plugins/master/$plugin.py" -o "$plugin.py" 2>/dev/null
done
```

> Nota: alguns plugins são de repos externos e podem precisar ser baixados manualmente se a URL acima falhar. Buscar por `$plugin.py qbittorrent search plugin` no GitHub.

## Lista completa dos 52 plugins
academictorrents, acgrip, ali213, anidex, animetosho, audiobookbay, bitsearch, bt4gprx, btdig, calidadtorrent, cloudtorrents, cpasbien, darklibria, divxtotal, dmhy, dodi_repacks, dontorrent, elitetorrent, esmeraldatorrent, fitgirl_repacks, glotorrents, kickasstorrents, linuxtracker, magnetdl, maxitorrent, mejortorrent, mikan, naranjatorrent, nyaa, nyaasi, onlinefix, pediatorrent, pirateiro, rockbox, rutor, sktorrent, smallgames, snowfl, solidtorrents, subsplease, thepiratebay, therarbg, tomadivx, torrent9, torrentdownload, torrentdownloads, torrentgalaxy, uniondht, yggtracker, yourbittorrent, yts, zooqle

## Plugins excluídos intencionalmente
mypornclub, xxxclubto, sukebeisi, sukebei, pantsu, traht + sites privados

## Plugin problemático
`tokyotoshokan.py` — causa `AttributeError: no attribute 'name'` e impede o qBittorrent de abrir. Nunca instalar.

**Why:** Lista exata dos plugins ativos para recriar o estado sem precisar refazer as exclusões manualmente.
**How to apply:** Ao receber pedido de reinstalação do qBittorrent, usar o script acima e nunca instalar tokyotoshokan.
