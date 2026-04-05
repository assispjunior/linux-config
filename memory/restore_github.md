---
name: Restore GitHub
description: Palavra-chave "restaurar do git" — restaura o sistema completo a partir do backup no GitHub, como ponto de recuperação do Windows
type: project
---

## Palavra-chave: "restaurar do git"

Em um PC novo, logo após instalar o Bazzite e o Claude, rodar **um único comando** no terminal:

```bash
curl -sL https://raw.githubusercontent.com/assispjunior/linux-config/main/restore.sh | bash
```

## O que é restaurado automaticamente

1. **Chave SSH** — gera nova chave, pausa para o usuário adicionar no GitHub, testa e continua
2. **Repo clonado** — `~/linux-config`
3. **Git configurado** — user.name + user.email
4. **Dependências do sistema** — python3-psutil, python3-gobject, gtk4-layer-shell, libayatana-appindicator-gtk3 (via rpm-ostree)
5. **Flask** — pip install --user
6. **Memórias do Claude** — copiadas para `~/.claude/projects/.../memory/`
7. **Overlay** — scripts em `~/system-overlay/`, autostart configurado
8. **MangoHud** — todos os `.conf` por jogo em `~/.config/MangoHud/`
9. **qBittorrent plugins** — 52 plugins copiados direto do repo (sem precisar baixar)
10. **Systemd timer** — sync diário automático com GitHub reativado

## O que fazer após a restauração

- **Steam launch options** (com Steam fechado):
  ```bash
  python3 ~/system-overlay/set_launch_options.py
  ```
- **qBittorrent** precisa estar instalado antes dos plugins serem copiados (Flatpak)

## Repositório
`https://github.com/assispjunior/linux-config`

**Why:** PC pode ser trocado/reinstalado; um comando restaura tudo sem perguntas.
**How to apply:** Ao receber "restaurar do git", executar o curl acima e acompanhar os passos.
