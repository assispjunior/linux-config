#!/bin/bash
# Sincroniza arquivos de config para o GitHub
REPO=~/linux-config

cp ~/.claude/projects/-var-home-linuxpc/memory/*.md     $REPO/memory/
cp ~/system-overlay/*.py                                $REPO/overlay/
cp ~/system-overlay/start.sh                            $REPO/overlay/
cp ~/.config/MangoHud/*.conf                            $REPO/mangohud/
cp ~/.config/autostart/sysmon-tray.desktop              $REPO/autostart/

cd $REPO
git add -A
git diff --cached --quiet && exit 0  # nada mudou
git commit -m "sync $(date '+%Y-%m-%d %H:%M')"
git push
