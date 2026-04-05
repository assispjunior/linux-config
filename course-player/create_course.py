#!/usr/bin/env python3
"""
Cria um course player completo para qualquer curso.
Uso: python3 create_course.py "Nome do Curso" "/caminho/para/o/curso"
"""
import sys
import os
import re
import socket
from pathlib import Path

def find_free_port(start=5001):
    port = start
    while port < 5100:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('127.0.0.1', port)) != 0:
                return port
        port += 1
    return port

def slugify(name):
    return re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')

def create(course_name, course_dir):
    course_dir = os.path.expanduser(course_dir)
    if not os.path.isdir(course_dir):
        print(f"Erro: diretório não encontrado: {course_dir}")
        sys.exit(1)

    slug = slugify(course_name)
    app_dir = os.path.expanduser(f"~/.local/share/course-player-{slug}")
    port = find_free_port(5001)

    os.makedirs(f"{app_dir}/templates", exist_ok=True)

    # ── app.py ───────────────────────────────────────────────────────────────
    app_py = f'''from flask import Flask, render_template, jsonify, request, send_file, abort
import os, re, json, threading
from pathlib import Path

app = Flask(__name__)

COURSE_DIR   = {repr(course_dir)}
PROGRESS_FILE = os.path.join(os.path.dirname(__file__), "progress.json")
VIDEO_EXTENSIONS = {{'.mp4', '.mkv', '.avi', '.webm', '.mov', '.m4v'}}

def natural_key(path):
    name = path.name
    match = re.match(r'^(\\d+)', name)
    return (int(match.group(1)) if match else float('inf'), name.lower())

def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE) as f: return json.load(f)
    return {{}}

def save_progress(data):
    with open(PROGRESS_FILE, 'w') as f: json.dump(data, f, indent=2)

def get_course_structure():
    sections = []
    for section_dir in sorted(Path(COURSE_DIR).iterdir(), key=natural_key):
        if not section_dir.is_dir(): continue
        lessons = []
        for lesson_dir in sorted((d for d in section_dir.iterdir() if d.is_dir()), key=natural_key):
            video_file = description_file = None
            materials = []
            for f in sorted(lesson_dir.iterdir()):
                if f.is_file() and f.suffix.lower() in VIDEO_EXTENSIONS:
                    if video_file is None: video_file = str(f.relative_to(COURSE_DIR))
                elif f.is_file() and f.name in ('descricao.html', 'links.html'):
                    description_file = str(f.relative_to(COURSE_DIR))
                elif f.is_dir() and f.name == '00. Materiais':
                    for m in sorted(f.iterdir()):
                        if m.is_file(): materials.append({{'name': m.name, 'path': str(m.relative_to(COURSE_DIR))}})
            if video_file or description_file:
                lessons.append({{'id': str(lesson_dir.relative_to(COURSE_DIR)), 'name': lesson_dir.name,
                                  'video': video_file, 'description': description_file, 'materials': materials}})
        if lessons: sections.append({{'id': str(section_dir.relative_to(COURSE_DIR)), 'name': section_dir.name, 'lessons': lessons}})
    return sections

@app.route('/')
def index(): return render_template('index.html')

@app.route('/api/course')
def api_course(): return jsonify(get_course_structure())

@app.route('/api/progress')
def api_get_progress(): return jsonify(load_progress())

@app.route('/api/progress', methods=['POST'])
def api_set_progress():
    data = request.json; progress = load_progress()
    progress[data['lesson_id']] = data['watched']; save_progress(progress)
    return jsonify({{'ok': True}})

@app.route('/api/play', methods=['POST'])
def api_play():
    import subprocess
    data = request.json
    full_path = os.path.join(COURSE_DIR, data.get('video_path', ''))
    lesson_id = data.get('lesson_id')
    if not os.path.exists(full_path): return jsonify({{'ok': False}}), 404
    def run_player():
        try:
            subprocess.run(['flatpak', 'run', 'org.kde.haruna', full_path],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if lesson_id:
                prog = load_progress(); prog[lesson_id] = True; save_progress(prog)
        except Exception: pass
    threading.Thread(target=run_player, daemon=True).start()
    return jsonify({{'ok': True}})

@app.route('/file/<path:filepath>')
def serve_file(filepath):
    full_path = os.path.join(COURSE_DIR, filepath)
    if not os.path.exists(full_path): abort(404)
    return send_file(full_path)

if __name__ == '__main__':
    import webbrowser
    threading.Timer(1.2, lambda: webbrowser.open('http://127.0.0.1:{port}')).start()
    app.run(debug=False, host='127.0.0.1', port={port}, use_reloader=False)
'''
    with open(f"{app_dir}/app.py", "w") as f:
        f.write(app_py)

    # ── index.html ───────────────────────────────────────────────────────────
    index_html = open(Path(__file__).parent / "index_template.html").read()
    index_html = index_html.replace("{{COURSE_NAME}}", course_name)
    with open(f"{app_dir}/templates/index.html", "w") as f:
        f.write(index_html)

    # ── start.sh ─────────────────────────────────────────────────────────────
    start_sh = f'''#!/bin/bash
if curl -s http://127.0.0.1:{port} > /dev/null 2>&1; then
    xdg-open http://127.0.0.1:{port}
    exit 0
fi
cd "$(dirname "$0")"
nohup python3 app.py > /tmp/{slug}.log 2>&1 &
'''
    with open(f"{app_dir}/start.sh", "w") as f:
        f.write(start_sh)
    os.chmod(f"{app_dir}/start.sh", 0o755)

    # ── progress.json ─────────────────────────────────────────────────────────
    if not os.path.exists(f"{app_dir}/progress.json"):
        with open(f"{app_dir}/progress.json", "w") as f:
            f.write("{}")

    # ── desktop launcher ─────────────────────────────────────────────────────
    desktop = f"""[Desktop Entry]
Type=Application
Name={course_name}
Exec=/bin/bash {app_dir}/start.sh
Icon=applications-education
Terminal=false
Categories=Education;
"""
    desktop_path = os.path.expanduser(f"~/.local/share/applications/{slug}.desktop")
    with open(desktop_path, "w") as f:
        f.write(desktop)

    print(f"✓ Course player criado em {app_dir}")
    print(f"✓ Porta: {port}")
    print(f"✓ Launcher: {desktop_path}")
    print(f"\nIniciando...")
    os.system(f"bash {app_dir}/start.sh")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python3 create_course.py \"Nome do Curso\" \"/caminho/do/curso\"")
        sys.exit(1)
    create(sys.argv[1], sys.argv[2])
