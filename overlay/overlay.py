#!/usr/bin/env python3
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Gtk4LayerShell", "1.0")
from gi.repository import Gtk, GLib, Gdk, Gtk4LayerShell, Gio
import psutil
import subprocess
import glob
import re
import os
import signal
import csv

PID_FILE = "/tmp/system-overlay.pid"

# ── MangoHud FPS limits ──────────────────────────────────────────────────────
GLOBAL_CONF   = "/home/linuxpc/.config/MangoHud/MangoHud.conf"
MHUD_CONF_DIR = "/home/linuxpc/.config/MangoHud"

def parse_fps_limits():
    try:
        with open(GLOBAL_CONF) as f:
            for line in f:
                if line.startswith("fps_limit="):
                    vals = line.strip().split("=")[1].split(",")
                    limits = [int(v) for v in vals if v.strip().isdigit()]
                    return limits + [0]
    except Exception:
        pass
    return [60, 82, 162, 0]

FPS_LIMITS = parse_fps_limits()
fps_limit_index = 0

def detect_active_fps_limit():
    """Lê o fps_limit do config do jogo ativo (via MANGOHUD_CONFIGFILE no /proc)."""
    try:
        for env_file in glob.glob("/proc/*/environ"):
            try:
                with open(env_file, "rb") as f:
                    env = f.read().decode("utf-8", errors="replace")
                if "MangoHud" not in env and "MANGOHUD" not in env:
                    continue
                cfg_match = re.search(r'MANGOHUD_CONFIGFILE=([^\x00]+)', env)
                if cfg_match:
                    cfg_path = cfg_match.group(1)
                    with open(cfg_path) as f:
                        for line in f:
                            if line.startswith("fps_limit="):
                                vals = [int(v) for v in line.strip().split("=")[1].split(",")
                                        if v.strip().isdigit()]
                                return vals[0] if vals else None
            except Exception:
                pass
    except Exception:
        pass
    return None

def current_fps_label():
    val = FPS_LIMITS[fps_limit_index]
    return "SEM LIMITE" if val == 0 else f"{val} FPS"

# ── Leitura de hardware ──────────────────────────────────────────────────────
def read_file(path):
    try:
        with open(path) as f:
            return f.read().strip()
    except Exception:
        return None

def get_gpu_load():
    v = read_file("/sys/class/drm/card1/device/gpu_busy_percent")
    return int(v) if v else 0

def get_gpu_temp():
    v = read_file("/sys/class/hwmon/hwmon2/temp1_input")
    return int(v) // 1000 if v else 0

def get_gpu_vram():
    used = read_file("/sys/class/drm/card1/device/mem_info_vram_used")
    total = read_file("/sys/class/drm/card1/device/mem_info_vram_total")
    if used and total:
        return int(used) / 1024**3, int(total) / 1024**3
    return 0, 0

def get_cpu_load():
    return psutil.cpu_percent(interval=None)

def get_cpu_temp():
    v = read_file("/sys/class/hwmon/hwmon3/temp1_input")
    return int(v) // 1000 if v else 0

def get_ram():
    mem = psutil.virtual_memory()
    return mem.used / 1024**3, mem.total / 1024**3, mem.percent

def get_nvme_temp():
    v = read_file("/sys/class/hwmon/hwmon1/temp1_input")
    return int(v) // 1000 if v else 0

MHUD_LOG_DIR = "/tmp/mhud"
_mhud_cache = {"file": None, "fps_col": -1, "low1_col": -1}

def get_mhud_log_file():
    files = glob.glob(f"{MHUD_LOG_DIR}/*.csv")
    if not files:
        return None
    return max(files, key=os.path.getmtime)

def get_fps_data():
    """Retorna (fps_atual, 1%_low) do log mais recente do MangoHud."""
    try:
        log = get_mhud_log_file()
        if not log:
            return None, None

        # Relê o arquivo só se mudou
        if _mhud_cache["file"] != log:
            _mhud_cache["file"] = log
            _mhud_cache["fps_col"] = -1
            _mhud_cache["low1_col"] = -1

        with open(log, "r") as f:
            lines = f.readlines()

        # Encontra a linha de cabeçalho (fps,frametime,...)
        header_idx = None
        for i, line in enumerate(lines):
            if line.startswith("fps,"):
                header_idx = i
                break
        if header_idx is None:
            return None, None

        headers = lines[header_idx].strip().split(",")
        fps_col = headers.index("fps") if "fps" in headers else -1
        # 1% low pode vir como "0.01_low" ou "1%_low"
        low1_col = -1
        for h in ["0.01_low", "1%_low", "fps_0.01"]:
            if h in headers:
                low1_col = headers.index(h)
                break

        data_lines = [l.strip() for l in lines[header_idx+1:] if l.strip() and not l.startswith("#")]
        if not data_lines:
            return None, None

        last = data_lines[-1].split(",")

        fps = float(last[fps_col]) if fps_col >= 0 and fps_col < len(last) else None

        # 1% low: usa o valor da coluna se existir, senão calcula dos últimos 60 samples
        low1 = None
        if low1_col >= 0 and low1_col < len(last):
            try:
                low1 = float(last[low1_col])
            except Exception:
                pass
        if low1 is None and fps_col >= 0:
            samples = []
            for l in data_lines[-120:]:
                parts = l.split(",")
                try:
                    samples.append(float(parts[fps_col]))
                except Exception:
                    pass
            if samples:
                samples.sort()
                idx = max(0, int(len(samples) * 0.01) - 1)
                low1 = samples[idx]

        return fps, low1
    except Exception:
        return None, None

def get_mangohud_active():
    try:
        for maps_file in glob.glob("/proc/*/maps"):
            try:
                with open(maps_file, "r") as f:
                    if "MangoHud" in f.read():
                        return True
            except Exception:
                pass
    except Exception:
        pass
    return False

# ── Cores ────────────────────────────────────────────────────────────────────
COLOR_YELLOW  = "#f0c040"
COLOR_RED     = "#e05050"
COLOR_CYAN    = "#40d0d0"
COLOR_GREEN   = "#50d080"
COLOR_DIM     = "#888888"
COLOR_BLUE    = "#4da6ff"
COLOR_ORANGE  = "#ff8c00"

# ── Black Mode ───────────────────────────────────────────────────────────────
_black_mode_on  = False
_brightness_bak = 100  # guarda o brilho original

def black_mode_toggle():
    global _black_mode_on, _brightness_bak
    if not _black_mode_on:
        # Ler brilho atual antes de apagar
        try:
            out = subprocess.check_output(
                ["ddcutil", "--display", "1", "getvcp", "10"],
                stderr=subprocess.DEVNULL
            ).decode()
            import re as _re
            m = _re.search(r"current value\s*=\s*(\d+)", out)
            if m:
                _brightness_bak = int(m.group(1))
        except Exception:
            _brightness_bak = 100

        # Minimizar todas as janelas (show desktop KDE)
        subprocess.Popen(["qdbus", "org.kde.KWin", "/KWin", "showDesktop", "1"],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        # Brilho 10%
        subprocess.Popen(["ddcutil", "--display", "1", "setvcp", "10", "10"],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        _black_mode_on = True
    else:
        # Restaurar brilho
        subprocess.Popen(["ddcutil", "--display", "1", "setvcp", "10", str(_brightness_bak)],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        # Desfazer show desktop
        subprocess.Popen(["qdbus", "org.kde.KWin", "/KWin", "showDesktop", "0"],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        _black_mode_on = False
    return _black_mode_on

# Thresholds por componente: (limite_medio, limite_alto)
TEMP_THRESHOLDS = {
    "cpu":   (60, 80),
    "gpu":   (60, 75),
    "nvme":  (45, 60),
}

def temp_color(component, value):
    low, high = TEMP_THRESHOLDS[component]
    if value < low:
        return COLOR_BLUE
    elif value < high:
        return COLOR_ORANGE
    else:
        return COLOR_RED

# ── Construção da UI ─────────────────────────────────────────────────────────
class OverlayWindow(Gtk.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app)
        self.set_decorated(False)
        self.set_resizable(False)
        self._visible = True

        # Layer shell — monitor HDMI-A-1 (segundo monitor, portrait)
        Gtk4LayerShell.init_for_window(self)
        Gtk4LayerShell.set_layer(self, Gtk4LayerShell.Layer.OVERLAY)
        Gtk4LayerShell.set_keyboard_mode(self, Gtk4LayerShell.KeyboardMode.NONE)
        Gtk4LayerShell.set_exclusive_zone(self, -1)
        Gtk4LayerShell.set_anchor(self, Gtk4LayerShell.Edge.BOTTOM, True)
        Gtk4LayerShell.set_anchor(self, Gtk4LayerShell.Edge.RIGHT, True)
        Gtk4LayerShell.set_margin(self, Gtk4LayerShell.Edge.BOTTOM, 20)
        Gtk4LayerShell.set_margin(self, Gtk4LayerShell.Edge.RIGHT, 20)

        # Pinnar no segundo monitor (portrait, x=0)
        display = Gdk.Display.get_default()
        monitors = display.get_monitors()
        for i in range(monitors.get_n_items()):
            m = monitors.get_item(i)
            geo = m.get_geometry()
            if geo.x == 0 and geo.height > geo.width:
                Gtk4LayerShell.set_monitor(self, m)
                break

        # CSS
        css = Gtk.CssProvider()
        css.load_from_string("""
            window {
                background-color: rgba(0, 0, 0, 0.75);
                border-radius: 12px;
            }
            .section-label {
                font-family: monospace;
                font-size: 11px;
                color: #aaaaaa;
                letter-spacing: 2px;
            }
            .unit-label {
                font-family: monospace;
                font-size: 12px;
                color: #888888;
            }
            .fps-button {
                font-family: monospace;
                font-size: 16px;
                font-weight: bold;
                background-color: rgba(255,255,255,0.08);
                border: 1px solid rgba(255,255,255,0.15);
                border-radius: 8px;
                padding: 6px 16px;
                color: #50d080;
            }
            .fps-button:hover {
                background-color: rgba(255,255,255,0.15);
            }
            separator {
                background-color: rgba(255,255,255,0.12);
                min-height: 1px;
            }
        """)
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(), css,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        # Layout principal
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        main_box.set_margin_top(16)
        main_box.set_margin_bottom(16)
        main_box.set_margin_start(20)
        main_box.set_margin_end(20)

        # GPU
        main_box.append(self._section("GPU"))
        gpu_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        self.lbl_gpu_load = self._value_label("0%", COLOR_YELLOW)
        self.lbl_gpu_temp = self._value_label("0°", COLOR_RED)
        self.lbl_gpu_vram = self._value_label("0.0G", COLOR_GREEN)
        gpu_row.append(self._stat_col(self.lbl_gpu_load, "LOAD"))
        gpu_row.append(self._stat_col(self.lbl_gpu_temp, "TEMP"))
        gpu_row.append(self._stat_col(self.lbl_gpu_vram, "VRAM"))
        main_box.append(gpu_row)
        main_box.append(Gtk.Separator())

        # CPU
        main_box.append(self._section("CPU"))
        cpu_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        self.lbl_cpu_load = self._value_label("0%", COLOR_YELLOW)
        self.lbl_cpu_temp = self._value_label("0°", COLOR_RED)
        cpu_row.append(self._stat_col(self.lbl_cpu_load, "LOAD"))
        cpu_row.append(self._stat_col(self.lbl_cpu_temp, "TEMP"))
        main_box.append(cpu_row)
        main_box.append(Gtk.Separator())

        # RAM
        main_box.append(self._section("RAM"))
        self.lbl_ram = self._value_label("0.0G", COLOR_GREEN)
        main_box.append(self._stat_col(self.lbl_ram, "USO"))
        main_box.append(Gtk.Separator())

        # NVMe
        main_box.append(self._section("NVMe"))
        self.lbl_nvme_temp = self._value_label("0°", COLOR_RED)
        main_box.append(self._stat_col(self.lbl_nvme_temp, "TEMP"))
        main_box.append(Gtk.Separator())

        # FPS
        main_box.append(self._section("FPS"))
        fps_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        self.lbl_fps      = self._value_label("—", COLOR_CYAN)
        self.lbl_fps_low1 = self._value_label("—", COLOR_DIM)
        fps_row.append(self._stat_col(self.lbl_fps,      "ATUAL"))
        fps_row.append(self._stat_col(self.lbl_fps_low1, "1% LOW"))
        main_box.append(fps_row)
        main_box.append(Gtk.Separator())

        # FPS Limit
        main_box.append(self._section("FPS LIMIT"))
        self.fps_btn = Gtk.Button(label=current_fps_label())
        self.fps_btn.add_css_class("fps-button")
        self.fps_btn.connect("clicked", self._on_fps_clicked)
        main_box.append(self.fps_btn)
        main_box.append(Gtk.Separator())

        # MangoHud status
        main_box.append(self._section("MANGOHUD"))
        self.lbl_mango = Gtk.Label()
        self.lbl_mango.set_halign(Gtk.Align.START)
        self._update_mango_label(False)
        main_box.append(self.lbl_mango)

        main_box.append(Gtk.Separator())

        # Black Mode
        self.black_btn = Gtk.Button(label="☾  BLACK MODE")
        self.black_btn.add_css_class("fps-button")
        self.black_btn.connect("clicked", self._on_black_clicked)
        main_box.append(self.black_btn)

        self.set_child(main_box)

        # SIGUSR1 = toggle visibilidade (enviado pelo tray)
        GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, signal.SIGUSR1, self._toggle_visible)

        psutil.cpu_percent(interval=None)
        GLib.timeout_add(1000, self._update)

    def _section(self, text):
        lbl = Gtk.Label(label=text)
        lbl.add_css_class("section-label")
        lbl.set_halign(Gtk.Align.START)
        return lbl

    def _value_label(self, text, color_hex):
        lbl = Gtk.Label()
        lbl.set_markup(self._mk(text, color_hex))
        return lbl

    def _mk(self, text, color_hex):
        return f'<span color="{color_hex}" font_family="monospace" font_size="20480" font_weight="bold">{text}</span>'

    def _stat_col(self, value_lbl, sub_text):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        box.append(value_lbl)
        sub = Gtk.Label(label=sub_text)
        sub.add_css_class("unit-label")
        sub.set_halign(Gtk.Align.CENTER)
        box.append(sub)
        return box

    def _set_val(self, lbl, text, color_hex):
        lbl.set_markup(self._mk(text, color_hex))

    def _update(self):
        gpu_load = get_gpu_load()
        gpu_temp = get_gpu_temp()
        vram_used, _ = get_gpu_vram()
        cpu_load = get_cpu_load()
        cpu_temp = get_cpu_temp()
        ram_used, _, ram_pct = get_ram()
        nvme_temp = get_nvme_temp()

        self._set_val(self.lbl_gpu_load, f"{gpu_load}%",         COLOR_YELLOW)
        self._set_val(self.lbl_gpu_temp, f"{gpu_temp}°",         temp_color("gpu",  gpu_temp))
        self._set_val(self.lbl_gpu_vram, f"{vram_used:.1f}G",    COLOR_GREEN)
        self._set_val(self.lbl_cpu_load, f"{cpu_load:.0f}%",     COLOR_YELLOW)
        self._set_val(self.lbl_cpu_temp, f"{cpu_temp}°",         temp_color("cpu",  cpu_temp))
        self._set_val(self.lbl_ram,      f"{ram_used:.1f}G  {ram_pct:.0f}%", COLOR_GREEN)
        self._set_val(self.lbl_nvme_temp,f"{nvme_temp}°",        temp_color("nvme", nvme_temp))
        fps, low1 = get_fps_data()
        if fps is not None:
            self._set_val(self.lbl_fps,      f"{fps:.0f}",  COLOR_CYAN)
            self._set_val(self.lbl_fps_low1, f"{low1:.0f}" if low1 is not None else "—", COLOR_DIM)
        else:
            self._set_val(self.lbl_fps,      "—", COLOR_DIM)
            self._set_val(self.lbl_fps_low1, "—", COLOR_DIM)

        mango_active = get_mangohud_active()
        self._update_mango_label(mango_active)

        # Sincroniza FPS LIMIT com o config do jogo ativo
        if mango_active:
            detected = detect_active_fps_limit()
            if detected is not None:
                global fps_limit_index
                if detected == 0 and 0 in FPS_LIMITS:
                    fps_limit_index = FPS_LIMITS.index(0)
                elif detected in FPS_LIMITS:
                    fps_limit_index = FPS_LIMITS.index(detected)
                else:
                    fps_limit_index = 0
                self.fps_btn.set_label(current_fps_label())

        return True

    def _update_mango_label(self, active):
        if active:
            self.lbl_mango.set_markup(self._mk("ON",  "#50d080"))
        else:
            self.lbl_mango.set_markup(
                f'<span color="#888888" font_family="monospace" font_size="20480">OFF</span>'
            )

    def _toggle_visible(self):
        try:
            if self._visible:
                self.set_visible(False)
            else:
                self.set_visible(True)
            self._visible = not self._visible
        except Exception as e:
            with open("/tmp/overlay_toggle.log", "a") as f:
                f.write(f"toggle error: {e}\n")
        return GLib.SOURCE_CONTINUE

    def _on_black_clicked(self, btn):
        on = black_mode_toggle()
        btn.set_label("☀  RESTAURAR" if on else "☾  BLACK MODE")

    def _on_fps_clicked(self, btn):
        global fps_limit_index
        fps_limit_index = (fps_limit_index + 1) % len(FPS_LIMITS)
        btn.set_label(current_fps_label())
        try:
            subprocess.Popen(["ydotool", "key", "shift+f1"],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass


class OverlayApp(Gtk.Application):
    def __init__(self):
        super().__init__(
            application_id="com.overlay.sysstats",
            flags=Gio.ApplicationFlags.NON_UNIQUE,
        )

    def do_activate(self):
        win = OverlayWindow(self)
        win.present()
        with open(PID_FILE, "w") as f:
            f.write(str(os.getpid()))

    def do_shutdown(self):
        try:
            os.remove(PID_FILE)
        except Exception:
            pass
        Gtk.Application.do_shutdown(self)


if __name__ == "__main__":
    app = OverlayApp()
    app.run()
