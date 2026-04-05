#!/bin/bash
# ============================================================
#  RESTAURAÇÃO COMPLETA DO LINUX — assispjunior/linux-config
#  Como usar em PC novo (sem nada configurado):
#    curl -sL https://raw.githubusercontent.com/assispjunior/linux-config/main/restore.sh | bash
# ============================================================
set -e

REPO_URL="git@github.com:assispjunior/linux-config.git"
REPO_HTTPS="https://github.com/assispjunior/linux-config.git"
REPO=~/linux-config
GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'

ok()   { echo -e "${GREEN}✓ $1${NC}"; }
info() { echo -e "${YELLOW}→ $1${NC}"; }
err()  { echo -e "${RED}✗ $1${NC}"; }

echo ""
echo "=================================================="
echo "   RESTAURAÇÃO COMPLETA DO SISTEMA"
echo "=================================================="
echo ""

# ── 1. Chave SSH ─────────────────────────────────────────────
info "[1/9] Configurando chave SSH para GitHub..."
if [ ! -f ~/.ssh/github_backup ]; then
    ssh-keygen -t ed25519 -C "bazzite-backup" -f ~/.ssh/github_backup -N "" -q
    ok "Chave gerada"
else
    ok "Chave SSH já existe"
fi

# Garantir config SSH
if ! grep -q "github_backup" ~/.ssh/config 2>/dev/null; then
    mkdir -p ~/.ssh && chmod 700 ~/.ssh
    cat >> ~/.ssh/config << 'EOF'

Host github.com
  IdentityFile ~/.ssh/github_backup
  User git
EOF
fi

# Testar conexão SSH
if ! ssh -T git@github.com 2>&1 | grep -q "successfully authenticated"; then
    echo ""
    echo -e "${YELLOW}═══════════════════════════════════════════════════════${NC}"
    echo -e "${YELLOW} AÇÃO NECESSÁRIA — adicione a chave abaixo no GitHub:${NC}"
    echo -e "${YELLOW} github.com → Settings → SSH and GPG keys → New SSH key${NC}"
    echo -e "${YELLOW}═══════════════════════════════════════════════════════${NC}"
    echo ""
    cat ~/.ssh/github_backup.pub
    echo ""
    read -p "Pressione ENTER após adicionar a chave no GitHub..."
    if ! ssh -T git@github.com 2>&1 | grep -q "successfully authenticated"; then
        err "Autenticação falhou. Verifique a chave no GitHub e tente novamente."
        exit 1
    fi
fi
ok "SSH autenticado"

# ── 2. Clonar repo ───────────────────────────────────────────
info "[2/9] Clonando repositório..."
if [ -d "$REPO/.git" ]; then
    git -C "$REPO" pull --quiet
    ok "Repo atualizado"
else
    git clone "$REPO_URL" "$REPO" --quiet
    ok "Repo clonado"
fi

# ── 3. Git config ────────────────────────────────────────────
info "[3/9] Configurando git..."
git config --global user.name  "assispjunior"
git config --global user.email "assispjunior@users.noreply.github.com"
ok "Git configurado"

# ── 4. Dependências do sistema ───────────────────────────────
info "[4/9] Instalando dependências do sistema..."
PKGS=""
rpm -q python3-psutil               &>/dev/null || PKGS="$PKGS python3-psutil"
rpm -q python3-gobject              &>/dev/null || PKGS="$PKGS python3-gobject"
rpm -q gtk4-layer-shell             &>/dev/null || PKGS="$PKGS gtk4-layer-shell"
rpm -q gtk4-layer-shell-devel       &>/dev/null || PKGS="$PKGS gtk4-layer-shell-devel"
rpm -q libayatana-appindicator-gtk3 &>/dev/null || PKGS="$PKGS libayatana-appindicator-gtk3"

if [ -n "$PKGS" ]; then
    info "Instalando via rpm-ostree:$PKGS"
    rpm-ostree install --apply-live $PKGS
    ok "Pacotes instalados"
else
    ok "Dependências já instaladas"
fi

# Flask
if ! python3 -c "import flask" &>/dev/null; then
    info "Instalando Flask..."
    pip install flask --user -q
fi
ok "Flask disponível"

# ── 5. Memórias do Claude ────────────────────────────────────
info "[5/9] Restaurando memórias do Claude..."
CLAUDE_MEM=~/.claude/projects/-var-home-linuxpc/memory
mkdir -p "$CLAUDE_MEM"
cp "$REPO/memory/"*.md "$CLAUDE_MEM/"
ok "Memórias restauradas"

# ── 6. Overlay ───────────────────────────────────────────────
info "[6/9] Restaurando Overlay..."
mkdir -p ~/system-overlay
cp "$REPO/overlay/overlay.py"            ~/system-overlay/
cp "$REPO/overlay/tray.py"               ~/system-overlay/
cp "$REPO/overlay/start.sh"              ~/system-overlay/
cp "$REPO/overlay/set_launch_options.py" ~/system-overlay/
chmod +x ~/system-overlay/start.sh
ok "Overlay restaurado"

# ── 7. MangoHud ──────────────────────────────────────────────
info "[7/9] Restaurando configs MangoHud..."
mkdir -p ~/.config/MangoHud
cp "$REPO/mangohud/"*.conf ~/.config/MangoHud/
mkdir -p /tmp/mhud
ok "MangoHud restaurado"

# ── 8. qBittorrent plugins ───────────────────────────────────
info "[8/9] Restaurando plugins qBittorrent..."
QBIT_ENGINES=~/.var/app/org.qbittorrent.qBittorrent/data/qBittorrent/nova3/engines
if [ -d "$QBIT_ENGINES" ]; then
    cp "$REPO/qbittorrent/plugins/"*.py "$QBIT_ENGINES/"
    ok "$(ls $REPO/qbittorrent/plugins/*.py | wc -l) plugins restaurados"
else
    info "qBittorrent não instalado ainda — plugins ficam no repo para depois"
fi

# ── 9. Autostart + systemd ───────────────────────────────────
info "[9/9] Configurando autostart e sync automático..."
mkdir -p ~/.config/autostart
cp "$REPO/autostart/sysmon-tray.desktop" ~/.config/autostart/

mkdir -p ~/.config/systemd/user
cp "$REPO/systemd/linux-config-sync.service" ~/.config/systemd/user/
cp "$REPO/systemd/linux-config-sync.timer"   ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now linux-config-sync.timer
ok "Autostart e sync diário configurados"

# ── Iniciar overlay ──────────────────────────────────────────
echo ""
echo "=================================================="
ok "RESTAURAÇÃO CONCLUÍDA"
echo "=================================================="
echo ""
echo "Iniciando Overlay..."
bash ~/system-overlay/start.sh
echo ""
echo "Tudo pronto. O sistema está restaurado."
echo "Lembre-se de configurar as launch options do Steam (Steam deve estar fechado):"
echo "  python3 ~/system-overlay/set_launch_options.py"
echo ""
