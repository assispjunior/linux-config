---
name: Interface de Boot (GRUB)
description: rEFInd removido, GRUB padrão do Bazzite restaurado
type: project
---

## Status atual

- **rEFInd** desinstalado via `rpm-ostree uninstall rEFInd` em 2026-04-04
- `/etc/default/grub` customizado removido
- GRUB regenerado com configurações padrão do Bazzite
- Reboot necessário para aplicar a remoção do rEFInd

**Why:** Usuário decidiu manter apenas a interface padrão do Bazzite, sem customização de boot.
