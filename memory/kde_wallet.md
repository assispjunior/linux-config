---
name: KDE Wallet desativado
description: KDE Wallet (kwallet) desativado para não mostrar popup de criação de carteira
type: project
---

KDE Wallet desativado via `~/.config/kwalletrc` com `Enabled=false`.

**Why:** Popup do `xdg-desktop-portal` pedindo para criar wallet `kdewallet` aparecia indesejadamente.

**How to apply:** Se o popup voltar após updates ou reboot, rodar:
```
kwriteconfig5 --file kwalletrc --group Wallet --key Enabled false
```
Ou recriar o arquivo `~/.config/kwalletrc`:
```ini
[Wallet]
Enabled=false
First Use=false
```
