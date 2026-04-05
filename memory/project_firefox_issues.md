---
name: Firefox Issues (Fedora/Flatpak)
description: YouTube sem vídeo e sem som no Firefox Flatpak — causa, diagnóstico e fix aplicado
type: project
---

## Problema
YouTube não reproduzia nenhum vídeo (erro genérico de reprodução) e sem som no Firefox.

## Ambiente
- OS: Fedora 43 (kernel 6.17.7-ba28.fc43.x86_64)
- GPU: AMD Radeon RX 9060 XT (RDNA 4, gfx1200)
- Firefox: **Flatpak** `org.mozilla.firefox` v148.0.2 (não RPM)
- Áudio: PipeWire + PulseAudio compat — funcionando normalmente no sistema
- DRM: já estava ativado no Firefox
- ffmpeg e ffmpeg-libs: instalados
- mozilla-openh264: instalado durante troubleshooting (não resolveu sozinho)

## Causa raiz
Firefox instalado via **Flatpak** tem sandbox isolada — sem acesso ao VA-API (aceleração de vídeo) nem ao dispositivo DRI da GPU AMD por padrão.

## Fix aplicado
```bash
flatpak override --user --env=LIBVA_DRIVER_NAME=radeonsi --env=MOZ_ENABLE_WAYLAND=1 --device=dri org.mozilla.firefox
```

**Why:** Libera acesso ao `/dev/dri`, define o driver VA-API correto (radeonsi para AMD) e força Wayland nativo.

**How to apply:** Se Firefox Flatpak voltar a ter problemas de vídeo/áudio, verificar primeiro se as overrides ainda estão ativas com `flatpak override --user --show org.mozilla.firefox`.

## Status em 2026-04-03
Fix confirmado parcialmente: som voltou, vídeo aparentemente normalizado. Monitorando estabilidade.
