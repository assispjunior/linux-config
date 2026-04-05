---
name: Fifine AmpliGame D6 no Bazzite
description: Stream controller Fifine D6 — setup OpenDeck no Bazzite, o que foi feito e o que falta
type: project
---

O Fifine AmpliGame D6 é um stream controller (macro pad de 15 botões, 3×5, com RGB), **não é microfone nem gamepad**.

## Status
- USB ID: `3142:0007` — detectado pelo kernel (aparece no `lsusb`)
- Regra udev criada: `/etc/udev/rules.d/99-fifine-d6.rules`
- Usuário `linuxpc` adicionado ao grupo `plugdev`
- udev recarregado com `udevadm control --reload-rules && udevadm trigger`

**Why:** O software oficial do D6 só existe para Windows/Mac. No Linux a solução é o OpenDeck + plugin não-oficial da comunidade.

**How to apply:** Quando o usuário mencionar o D6, lembrar que o hardware já está reconhecido e que falta concluir a instalação do OpenDeck + plugin.

## O que FALTA fazer (pendente de logout/reboot)

1. Fazer logout/login para o grupo `plugdev` entrar em vigor
2. Instalar OpenDeck: `flatpak install flathub io.github.OpenDeck`
3. Baixar o plugin: https://github.com/shugotekitten/opendeck-ampgd6/releases
4. No OpenDeck: Plugins → Install from file → selecionar o `.zip`
5. Desconectar e reconectar o D6 fisicamente

## Referências
- Plugin não-oficial: https://github.com/shugotekitten/opendeck-ampgd6
- Fork alternativo: https://github.com/3dRikal/opendeck-ampgd6
