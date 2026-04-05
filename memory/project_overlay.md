---
name: Overlay
description: Widget de monitoramento do sistema (GPU/CPU/RAM/NVMe/FPS/MangoHud) no segundo monitor, com bandeja do sistema
type: project
---

Widget de monitoramento em tempo real para o segundo monitor (HDMI-A-1, portrait 1080x1920).

## Arquivos
- `/home/linuxpc/system-overlay/overlay.py` — janela GTK4 (widget principal)
- `/home/linuxpc/system-overlay/tray.py` — ícone na bandeja (GTK3 + AyatanaAppIndicator3)
- `/home/linuxpc/system-overlay/start.sh` — mata instâncias antigas e sobe o tray (que sobe o overlay)
- `~/.config/autostart/sysmon-tray.desktop` — autostart aponta para `start.sh`

## Como iniciar
```bash
bash /home/linuxpc/system-overlay/start.sh
```
Ou via autostart do KDE na próxima sessão.

## Visual
- Fundo semi-transparente, sem decoração, fixo no monitor (gtk4-layer-shell, Layer.OVERLAY)
- Seções: GPU (LOAD/TEMP/VRAM), CPU (LOAD/TEMP), RAM (USO), NVMe (TEMP), FPS (ATUAL/1% LOW), FPS LIMIT (botão), MANGOHUD (ON/OFF)
- Cores: amarelo=carga, vermelho=temp, ciano=FPS, verde=VRAM/RAM, cinza=inativo

## Stack
- Python + GTK4 + gtk4-layer-shell (Layer.OVERLAY, sem foco, always-on-top)
- LD_PRELOAD=/usr/lib64/libgtk4-layer-shell.so obrigatório
- GTK3 + AyatanaAppIndicator3 no processo separado do tray
- Comunicação tray→overlay via SIGUSR1 (toggle visibilidade) + PID em /tmp/system-overlay.pid

## Fontes de dados hardware
- GPU load: `/sys/class/drm/card1/device/gpu_busy_percent`
- GPU temp (edge): `/sys/class/hwmon/hwmon2/temp1_input`
- GPU VRAM: `/sys/class/drm/card1/device/mem_info_vram_{used,total}`
- CPU load: psutil.cpu_percent()
- CPU temp (Tctl): `/sys/class/hwmon/hwmon3/temp1_input`
- RAM: psutil.virtual_memory()
- NVMe temp (Composite): `/sys/class/hwmon/hwmon1/temp1_input`
- FPS / 1% low: lê CSV mais recente em `/tmp/mhud/` (log automático do MangoHud)
- MangoHud ativo: grep `/proc/*/maps` por "MangoHud"

## MangoHud integration
- `~/.config/MangoHud/MangoHud.conf` tem: `output_folder=/tmp/mhud`, `autostart_log=1`, `log_interval=500`
- FPS e 1% low mostram `—` quando nenhum jogo está rodando
- Botão FPS LIMIT cicla entre os valores do MangoHud.conf (60→82→162→SEM LIMITE) e envia Shift+F1 via ydotool
- MangoHud ON/OFF detectado por presença da lib nos `/proc/*/maps`

## Configuração MangoHud por jogo
- Script: `/home/linuxpc/system-overlay/set_launch_options.py` — aplica launch options no localconfig.vdf (rodar com Steam fechado)
- Configs por jogo em `~/.config/MangoHud/`: `overwatch.conf` (162), `hogwarts.conf` (82), `wuthering.conf` (82)
- Jogos configurados: Overwatch (2357570), Hogwarts Legacy (990080), Wuthering Waves (3513350)
- Launch option padrão: `MANGOHUD_CONFIGFILE=~/.config/MangoHud/{jogo}.conf gamemoderun mangohud %command%`
- **Palavra-chave:** "mangohud jogo" + nome + FPS limit → cria `.conf` e aplica launch option

## Status
Funcionando. Todos os recursos implementados.
