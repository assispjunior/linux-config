#!/bin/bash
# Reinstala o Overlay do zero a partir do backup no GitHub
set -e

REPO=~/linux-config
OVERLAY_DIR=~/system-overlay
AUTOSTART=~/.config/autostart

echo "=== Reinstall Overlay ==="

# 1. Atualizar repo
if [ -d "$REPO/.git" ]; then
    echo "[1/5] Atualizando repo..."
    git -C "$REPO" pull --quiet
else
    echo "[1/5] Clonando repo..."
    git clone git@github.com:assispjunior/linux-config.git "$REPO"
fi

# 2. Instalar dependências
echo "[2/5] Verificando dependências..."
PKGS=""
rpm -q python3-psutil            &>/dev/null || PKGS="$PKGS python3-psutil"
rpm -q python3-gobject           &>/dev/null || PKGS="$PKGS python3-gobject"
rpm -q gtk4-layer-shell          &>/dev/null || PKGS="$PKGS gtk4-layer-shell"
rpm -q gtk4-layer-shell-devel    &>/dev/null || PKGS="$PKGS gtk4-layer-shell-devel"
rpm -q libayatana-appindicator-gtk3 &>/dev/null || PKGS="$PKGS libayatana-appindicator-gtk3"

if [ -n "$PKGS" ]; then
    echo "    Instalando:$PKGS"
    rpm-ostree install --apply-live $PKGS
else
    echo "    Todas as dependências já instaladas."
fi

# 3. Copiar arquivos
echo "[3/5] Copiando arquivos..."
mkdir -p "$OVERLAY_DIR"
cp "$REPO/overlay/overlay.py"           "$OVERLAY_DIR/"
cp "$REPO/overlay/tray.py"              "$OVERLAY_DIR/"
cp "$REPO/overlay/start.sh"             "$OVERLAY_DIR/"
cp "$REPO/overlay/set_launch_options.py" "$OVERLAY_DIR/"
chmod +x "$OVERLAY_DIR/start.sh"

# 4. Autostart
echo "[4/5] Configurando autostart..."
mkdir -p "$AUTOSTART"
cp "$REPO/autostart/sysmon-tray.desktop" "$AUTOSTART/"

# 5. Iniciar
echo "[5/5] Iniciando..."
bash "$OVERLAY_DIR/start.sh"

echo ""
echo "=== Overlay reinstalado e rodando ==="
