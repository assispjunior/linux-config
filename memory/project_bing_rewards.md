---
name: Bing Rewards automation
description: Configuração completa da automação do Bing Rewards via Tampermonkey userscript
type: project
---

Userscript Tampermonkey instalado para automatizar o Bing Rewards quando o usuário abre o Firefox.

**Why:** Usuário esquecia de abrir o site manualmente todo dia para ganhar pontos.

**How to apply:** Quando o usuário mencionar "bing rewards", "rewards", "automação do bing" — resgatar este contexto.

## Arquivos criados
- Userscript: `~/.local/share/bing_rewards_session/bing_rewards.user.js`
- Script Playwright (desativado): `~/.local/bin/bing_rewards.py`
- Timer systemd (desativado): `~/.config/systemd/user/bing-rewards.timer`
- Sessão Playwright: `~/.local/share/bing_rewards_session/`

## Solução atual (ativa)
**Tampermonkey userscript** — roda no próprio Firefox do usuário quando abre `rewards.bing.com`.

O que faz:
1. Aguarda o Angular renderizar (polling até 30s) — resolve problema de timing com SPA
2. Clica nos cards de atividade via `.click()` com seletores: `mee-rewards-daily-set-item-content a`, `mee-rewards-more-activities-card a`, `mee-rewards-punchcard-partial a`
3. Faz 90 buscas no Bing com termos variados (navegação sequencial na mesma aba, delays 5–13s)
4. Marca como concluído no localStorage — não roda duas vezes no mesmo dia (reset à meia-noite local)

## Limitações conhecidas
- Cards tipo quiz/evento exigem interação manual na aba aberta — o script abre mas não controla o conteúdo da aba
- Buscas: 90/dia (máximo de pontos por busca)
- Versão atual: **6.1**

## Reset manual (quando diz "já feito hoje")
Cole no console do Firefox (F12) em qualquer página bing.com:
```javascript
localStorage.removeItem('bing_rewards_done_today');
localStorage.removeItem('bing_rewards_searches_done');
localStorage.removeItem('bing_rewards_searching_active');
```
Depois abre rewards.bing.com normalmente.

## Trigger
Firefox abre em `rewards.bing.com` porque foi definido como página inicial no perfil:
- Perfil: `~/.var/app/org.mozilla.firefox/config/mozilla/firefox/1gpaug75.default-release/prefs.js`
- `browser.startup.page = 1` (homepage, antes era 3 = restaurar sessão)
- `browser.startup.homepage = https://rewards.bing.com/`

## Histórico de decisões do script
- v3.1: GM_openInTab com seletores Angular — seletores não encontravam cards (timing)
- v4.0/5.0: window.open em links genéricos — abria trilhão de abas de login, corrompeu cookies
- **v6.0 (atual):** polling waitForCards + `.click()` — funciona; 90 buscas OK, maioria dos cards OK

## Histórico de projeto
- Tentamos Playwright headless (opção A) — funcionou tecnicamente mas risco de ban alto
- Tentamos systemd timer diário às 9h — desativado
- Escolhemos Tampermonkey (opção B) — mais seguro pois roda dentro do browser real do usuário
- Problema de login no Playwright: detecção de URL estava muito agressiva (corrigida mas abandonada)

## qBittorrent (contexto relacionado)
- Firefox instalado via Flatpak: `org.mozilla.firefox`
- qBittorrent instalado via Flatpak: `org.qbittorrent.qBittorrent`
