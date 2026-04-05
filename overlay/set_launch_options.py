#!/usr/bin/env python3
"""
Aplica launch options no Steam para jogos específicos.
Rodar com o Steam FECHADO.
"""
import shutil
from datetime import datetime

LOCALCONFIG = "/var/home/linuxpc/.local/share/Steam/userdata/860721594/config/localconfig.vdf"
MHUD_CFG    = "/home/linuxpc/.config/MangoHud"

GAMES = {
    "2357570": (f'MANGOHUD_CONFIGFILE={MHUD_CFG}/overwatch.conf gamemoderun mangohud %command%',  "Overwatch"),
    "990080":  (f'MANGOHUD_CONFIGFILE={MHUD_CFG}/hogwarts.conf gamemoderun mangohud %command%',   "Hogwarts Legacy"),
    "3513350": (f'MANGOHUD_CONFIGFILE={MHUD_CFG}/wuthering.conf gamemoderun mangohud %command%',  "Wuthering Waves"),
}

with open(LOCALCONFIG, "r", encoding="utf-8") as f:
    lines = f.readlines()

# Backup
backup = LOCALCONFIG + f".bak_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
shutil.copy2(LOCALCONFIG, backup)
print(f"Backup: {backup}\n")

def find_app_block(lines, appid):
    """
    Retorna (start_line, end_line) do bloco de apps que contém LastPlayed/Playtime.
    Ignora blocos que são dados binários (uma única linha com valor longo).
    """
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        # Linha com o appid como chave de bloco (sem valor na mesma linha)
        if line == f'"{appid}"':
            # Próxima linha não-vazia deve ser '{'
            j = i + 1
            while j < len(lines) and lines[j].strip() == "":
                j += 1
            if j < len(lines) and lines[j].strip() == "{":
                # Verifica se o bloco contém LastPlayed (bloco de apps)
                depth = 1
                k = j + 1
                has_lastplayed = False
                block_end = k
                while k < len(lines) and depth > 0:
                    s = lines[k].strip()
                    if s == "{":
                        depth += 1
                    elif s == "}":
                        depth -= 1
                        if depth == 0:
                            block_end = k
                    if "LastPlayed" in s or "Playtime" in s:
                        has_lastplayed = True
                    k += 1
                if has_lastplayed:
                    return j + 1, block_end  # linhas internas do bloco
        i += 1
    return None, None

output = list(lines)
offset = 0  # ajuste de índice após inserções

for appid, (launch_opt, name) in GAMES.items():
    start, end = find_app_block(output, appid)
    if start is None:
        print(f"  {name}: bloco não encontrado — defina manualmente:")
        print(f"    {launch_opt}")
        continue

    # Procura LaunchOptions dentro do bloco
    lo_line = None
    for idx in range(start, end):
        if '"LaunchOptions"' in output[idx]:
            lo_line = idx
            break

    indent = "\t\t\t\t\t\t"
    new_line = f'{indent}"LaunchOptions"\t\t"{launch_opt}"\n'

    if lo_line is not None:
        old = output[lo_line].strip()
        output[lo_line] = new_line
        print(f"  {name}: atualizado")
        print(f"    antes:  {old[:80]}")
        print(f"    depois: {new_line.strip()[:80]}")
    else:
        # Insere antes do fechamento do bloco
        output.insert(end, new_line)
        print(f"  {name}: adicionado — {new_line.strip()[:80]}")

with open(LOCALCONFIG, "w", encoding="utf-8") as f:
    f.writelines(output)

print("\nPronto. Pode abrir o Steam.")
