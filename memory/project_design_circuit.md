---
name: Create Course
description: Palavra-chave "Create Course [nome] [diretório]" — cria um course player completo (Flask + interface Hotmart) para qualquer curso local
type: project
---

## Palavra-chave

**"Create Course [Nome do Curso] [/caminho/do/curso]"**

Exemplo: `Create Course Blender Avançado /Linux_Storage/Media/Videos/Cursos/Blender`

## O que o comando faz

Executa sem perguntar nada:
```bash
python3 ~/linux-config/course-player/create_course.py "Nome do Curso" "/caminho/do/curso"
```

- Cria `~/.local/share/course-player-{slug}/` com app.py, templates/index.html, start.sh, progress.json
- Detecta porta livre automaticamente (a partir de 5001)
- Cria launcher `.desktop` no KDE
- Inicia o app imediatamente

## Cursos existentes

| Curso | Diretório | Porta | App dir |
|---|---|---|---|
| Design Circuit | `/var/home/linuxpc/Linux_Storage/Media/Videos/Cursos/Design Circuit` | 5000 | `~/.local/share/course-player/` |

## Stack
- Python + Flask
- Interface web estilo Hotmart (sidebar com seções/aulas, progresso, materiais)
- Vídeos abrem no Haruna (`flatpak run org.kde.haruna`) — Firefox Flatpak não decodifica H.264
- Auto-mark: aula marcada como vista quando Haruna fecha
- Ordenação natural numérica das seções/aulas

## Estrutura de curso esperada
```
Curso/
  1. Seção/
    1. Aula/
      video.mp4
      descricao.html   (opcional)
      links.html       (opcional)
      00. Materiais/   (opcional)
```

## Arquivos do gerador
- `~/linux-config/course-player/create_course.py` — script principal
- `~/linux-config/course-player/index_template.html` — template HTML com {{COURSE_NAME}}
