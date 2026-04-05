---
name: Restore GitHub
description: Como restaurar os arquivos de config e projetos do PC a partir do backup no GitHub após reinstalar o Claude
type: project
---

Repositório de backup: https://github.com/assispjunior/linux-config

## O que está salvo no repo

- `memory/` — todas as memórias do Claude (copiar para `~/.claude/projects/-var-home-linuxpc/memory/`)
- `overlay/` — código do Overlay (copiar para `~/system-overlay/`)
- `mangohud/` — configs MangoHud por jogo (copiar para `~/.config/MangoHud/`)
- `autostart/` — entrada de autostart do KDE (copiar para `~/.config/autostart/`)

## Passos para restaurar

```bash
# 1. Clonar o repo
git clone git@github.com:assispjunior/linux-config.git ~/linux-config

# 2. Restaurar memórias do Claude
mkdir -p ~/.claude/projects/-var-home-linuxpc/memory/
cp ~/linux-config/memory/*.md ~/.claude/projects/-var-home-linuxpc/memory/

# 3. Restaurar Overlay
mkdir -p ~/system-overlay/
cp ~/linux-config/overlay/* ~/system-overlay/
chmod +x ~/system-overlay/start.sh

# 4. Restaurar MangoHud
mkdir -p ~/.config/MangoHud/
cp ~/linux-config/mangohud/*.conf ~/.config/MangoHud/

# 5. Restaurar autostart
mkdir -p ~/.config/autostart/
cp ~/linux-config/autostart/*.desktop ~/.config/autostart/
```

## Pré-requisitos para o clone funcionar
- Chave SSH configurada: `~/.ssh/github_backup` adicionada em github.com → Settings → SSH keys
- Se a chave foi perdida, gerar nova: `ssh-keygen -t ed25519 -C "bazzite-backup" -f ~/.ssh/github_backup -N ""`
- Adicionar em `~/.ssh/config`:
  ```
  Host github.com
    IdentityFile ~/.ssh/github_backup
    User git
  ```

## Palavra-chave
Dizer **"restaurar do git"** para o Claude executar os passos acima automaticamente.

**Why:** PC pode ser reinstalado ou trocado; o GitHub é a fonte de verdade para todos os configs e projetos.
**How to apply:** Ao receber "restaurar do git", clonar o repo e copiar os arquivos nos destinos corretos.
