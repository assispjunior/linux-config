---
name: optimization
description: Rotina de verificação e correção silenciosa de todas as otimizações do sistema — rodar quando usuário digitar "optimization"
type: project
---

Quando o usuário disser "optimization", execute todas as verificações e correções abaixo sem explicar nada, apenas agindo. No final, mostre um resumo rápido do que estava OK e o que foi corrigido.

## 1. Firefox Flatpak — VA-API overrides

```bash
flatpak override --user --show org.mozilla.firefox | grep -q "LIBVA_DRIVER_NAME"
```
Se não retornar nada, reaplicar:
```bash
flatpak override --user --env=LIBVA_DRIVER_NAME=radeonsi --env=MOZ_ENABLE_WAYLAND=1 --device=dri org.mozilla.firefox
```

## 2. Firefox user.js — startup e media settings

Verificar que `~/.var/app/org.mozilla.firefox/config/mozilla/firefox/1gpaug75.default-release/user.js` contém:
- `browser.startup.page = 1`
- `browser.startup.homepage = https://rewards.bing.com/`
- `media.hardware-video-decoding.enabled = false` (RDNA 4 + Mesa < 26.1 — bugs)
- `media.ffmpeg.vaapi.enabled = false`
- `media.rdd-process.enabled = true`
- `media.rdd-ffvpx.enabled = true`

Se Mesa >= 26.1 (verificar com `glxinfo -B | grep Version`), pode reabilitar hardware decoding.

## 3. Plex Media Server — container rodando

```bash
systemctl --user is-active plex.service
```
Se inativo: `systemctl --user start plex.service`

Volumes montados em `~/.config/containers/systemd/plex.container`:
- `~/plex/config:/config`
- `~/plex/transcode:/transcode`
- `~/plex/media:/data`
- `~/Linux_Storage/Media/Videos/Filmes:/filmes:ro,z`
- `~/Linux_Storage/Media/Videos/Series:/series:ro,z`

## 4. GameMode — grupo e config

Verificar que usuário está no grupo gamemode:
```bash
groups linuxpc | grep gamemode
```
Se não: `sudo usermod -aG gamemode linuxpc` (requer reboot)

Verificar `/etc/gamemode.ini` contém seção `[gpu]` com `amd_performance_level=high` e `gpu_device=1`.

Verificar `~/.config/gamemode.ini` contém EPP scripts e não tem seção `[gpu]` duplicada.

## 5. sysctl gaming

```bash
sysctl vm.compaction_proactiveness vm.page_lock_unfairness
```
Esperado: `0` e `1`. Se diferente, reaplicar:
```bash
sudo sysctl -p /etc/sysctl.d/99-gaming.conf
```
Arquivo deve existir em `/etc/sysctl.d/99-gaming.conf`.

## 6. NVMe scheduler

```bash
cat /sys/block/nvme0n1/queue/scheduler
```
Esperado: `[none]`. Se não:
```bash
echo "none" | sudo tee /sys/block/nvme0n1/queue/scheduler
```
Verificar que `/etc/udev/rules.d/60-nvme-scheduler.rules` existe para persistir.

## 7. ffmpeg-full Flatpak

```bash
flatpak list | grep ffmpeg-full
```
Se não presente: `flatpak install -y flathub runtime/org.freedesktop.Platform.ffmpeg-full/x86_64/24.08`

## 8. Steam — launch options

```bash
grep "gamemoderun mangohud" ~/.local/share/Steam/userdata/*/config/localconfig.vdf
```
Jogos devem ter `gamemoderun mangohud %command%`.

## 9. Heroic — MangoHud e GameMode

```bash
grep -E "showMangohud|useGameMode" ~/.var/app/com.heroicgameslauncher.hgl/config/heroic/config.json
```
Esperado: `"showMangohud": true` e `"useGameMode": true`.

## 10. Eden — async_presentation

```bash
grep "async_presentation=" ~/.config/eden/qt-config.ini
```
Esperado: `async_presentation=true`.

## 11. EPP helper

Verificar `/etc/set-cpu-epp.sh` existe e é executável, e `/etc/sudoers.d/gamemode-epp` existe.

## 12. Bazzite — atualização disponível

```bash
ujust update 2>/dev/null || rpm-ostree upgrade --check 2>&1 | tail -3
```
Se houver atualização disponível, avisar o usuário.

## Setup do sistema (referência)
- OS: Bazzite 43 (OSTree imutável, KDE Kinoite)
- CPU: Ryzen 5 8600G
- GPU: AMD RX 9060 XT (RDNA 4, gfx1200, card1)
- RAM: 16GB + ZRAM 7.6GB
- Storage: NVMe (nvme0n1)
- Mesa: verificar versão atual — VA-API só seguro em >= 26.1
- Firefox: Flatpak org.mozilla.firefox, perfil `1gpaug75.default-release`
