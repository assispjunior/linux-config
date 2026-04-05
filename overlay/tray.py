#!/usr/bin/env python3
import gi
gi.require_version("Gtk", "3.0")
gi.require_version("AyatanaAppIndicator3", "0.1")
from gi.repository import Gtk, AyatanaAppIndicator3, GLib
import os
import signal
import subprocess

PID_FILE = "/tmp/system-overlay.pid"
OVERLAY_SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "overlay.py")
OVERLAY_LIB    = "/usr/lib64/libgtk4-layer-shell.so"

overlay_proc = None

def get_overlay_pid():
    try:
        with open(PID_FILE) as f:
            pid = int(f.read().strip())
        os.kill(pid, 0)  # verifica se está vivo
        return pid
    except Exception:
        return None

def start_overlay():
    global overlay_proc
    overlay_proc = subprocess.Popen(
        ["python3", OVERLAY_SCRIPT],
        env={**os.environ, "LD_PRELOAD": OVERLAY_LIB}
    )

def on_toggle(item):
    with open("/tmp/tray_debug.log", "a") as f:
        f.write("on_toggle chamado\n")
    pid = get_overlay_pid()
    with open("/tmp/tray_debug.log", "a") as f:
        f.write(f"pid encontrado: {pid}\n")
    if pid:
        os.kill(pid, signal.SIGUSR1)
        with open("/tmp/tray_debug.log", "a") as f:
            f.write(f"SIGUSR1 enviado para {pid}\n")
    else:
        start_overlay()
        with open("/tmp/tray_debug.log", "a") as f:
            f.write("start_overlay chamado\n")

def on_quit(item):
    pid = get_overlay_pid()
    if pid:
        os.kill(pid, signal.SIGTERM)
    Gtk.main_quit()

# ── Tray ─────────────────────────────────────────────────────────────────────
indicator = AyatanaAppIndicator3.Indicator.new(
    "system-overlay",
    "utilities-system-monitor",
    AyatanaAppIndicator3.IndicatorCategory.APPLICATION_STATUS,
)
indicator.set_status(AyatanaAppIndicator3.IndicatorStatus.ACTIVE)

menu = Gtk.Menu()

item_toggle = Gtk.MenuItem(label="Mostrar / Esconder")
item_toggle.connect("activate", on_toggle)
menu.append(item_toggle)

menu.append(Gtk.SeparatorMenuItem())

item_quit = Gtk.MenuItem(label="Sair")
item_quit.connect("activate", on_quit)
menu.append(item_quit)

menu.show_all()
indicator.set_menu(menu)

# Inicia o overlay ao abrir o tray
start_overlay()

Gtk.main()
