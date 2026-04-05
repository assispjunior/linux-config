---
name: Reinstall Overlay
description: Reinstalar o Overlay (widget GTK4 + bandeja) com um único comando a partir do backup no GitHub
type: project
---

Widget de monitoramento em tempo real para o segundo monitor (HDMI-A-1, portrait 1080x1920).

## Reinstalação — um comando

```bash
bash ~/linux-config/overlay/reinstall.sh
```

Se o repo não estiver clonado ainda:
```bash
git clone git@github.com:assispjunior/linux-config.git ~/linux-config && bash ~/linux-config/overlay/reinstall.sh
```

O script faz tudo: atualiza repo, instala dependências, copia arquivos, configura autostart e inicia.

## Arquivos
- `~/system-overlay/overlay.py` — janela GTK4 (widget principal)
- `~/system-overlay/tray.py` — ícone na bandeja (GTK3 + AyatanaAppIndicator3)
- `~/system-overlay/start.sh` — mata instâncias antigas e sobe o tray
- `~/.config/autostart/sysmon-tray.desktop` — autostart do KDE

## Dependências
- `python3-psutil`, `python3-gobject`
- `gtk4-layer-shell`, `gtk4-layer-shell-devel`
- `libayatana-appindicator-gtk3`
- LD_PRELOAD=/usr/lib64/libgtk4-layer-shell.so (já no start.sh)

## Visual
- Fundo semi-transparente, sem decoração, fixo no monitor (Layer.OVERLAY, always-on-top)
- Seções: GPU (LOAD/TEMP/VRAM), CPU (LOAD/TEMP), RAM (USO), NVMe (TEMP), FPS (ATUAL/1% LOW), FPS LIMIT (botão), MANGOHUD (ON/OFF)
- Temperaturas dinâmicas: azul=baixo, laranja=médio, vermelho=alto (thresholds por componente)

## Thresholds de temperatura
- CPU: azul <60°, laranja 60-80°, vermelho ≥80°
- GPU: azul <60°, laranja 60-75°, vermelho ≥75°
- NVMe: azul <45°, laranja 45-60°, vermelho ≥60°

## Hardware mapeado
- GPU load: `/sys/class/drm/card1/device/gpu_busy_percent`
- GPU temp: `/sys/class/hwmon/hwmon2/temp1_input` (edge)
- GPU VRAM: `/sys/class/drm/card1/device/mem_info_vram_{used,total}`
- CPU load: psutil.cpu_percent()
- CPU temp: `/sys/class/hwmon/hwmon3/temp1_input` (Tctl)
- RAM: psutil.virtual_memory()
- NVMe temp: `/sys/class/hwmon/hwmon1/temp1_input` (Composite)
- FPS / 1% low: CSV mais recente em `/tmp/mhud/`
- MangoHud ativo: grep `/proc/*/maps` por "MangoHud"

## MangoHud integration
- `~/.config/MangoHud/MangoHud.conf`: `output_folder=/tmp/mhud`, `autostart_log=1`, `log_interval=500`, `no_display`
- Botão FPS LIMIT cicla 60→82→162→SEM LIMITE e envia Shift+F1 via ydotool
- **Palavra-chave:** "mangohud jogo" + nome + FPS limit → cria `.conf` e aplica launch option no Steam

## Jogos configurados
- Overwatch (2357570) → overwatch.conf → 162 FPS
- Hogwarts Legacy (990080) → hogwarts.conf → 82 FPS
- Wuthering Waves (3513350) → wuthering.conf → 82 FPS
- Script de launch options: `~/system-overlay/set_launch_options.py` (rodar com Steam fechado)
