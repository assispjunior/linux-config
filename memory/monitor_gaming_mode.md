---
name: Monitor primário no Gaming Mode
description: Configuração do OUTPUT_CONNECTOR para o gamescope iniciar no monitor correto (DP-1)
type: project
---

## Problema
Bazzite Gaming Mode (gamescope/Big Picture) iniciava no monitor secundário (HDMI-A-1, 1920x1080) em vez do principal (DP-1, 2560x1440).

## Solução aplicada
Criado `~/.config/environment.d/gamescope-output.conf` com:
```
OUTPUT_CONNECTOR=DP-1
```

O script `/usr/share/gamescope-session-plus/gamescope-session-plus` lê esse arquivo e passa `--prefer-output DP-1` ao gamescope.

## Setup de monitores
- `DP-1` — 2560x1440 — **monitor principal**
- `HDMI-A-1` — 1920x1080 — monitor secundário

**Why:** gamescope escolhia o monitor errado por padrão (`OUTPUT_CONNECTOR` defaultava para `*,eDP-1`).
**How to apply:** Se o problema voltar após update do Bazzite, verificar se o arquivo ainda existe e se o conteúdo está correto.
