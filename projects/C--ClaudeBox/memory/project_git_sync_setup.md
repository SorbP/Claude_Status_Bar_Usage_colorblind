---
name: Git sync setup for Claude config
description: Claude config synkas via GitHub repo - hemmaдatorn behöver fortfarande kopplas upp
type: project
originSessionId: 18b54822-ad76-43b1-b6f4-bf2428d0d657
---
GitHub-repot `https://github.com/SorbP/Claude_Status_Bar_Usage_colorblind.git` innehåller Claude config (settings.json, memory, statusline med färgblindhetstema).

Den här maskinen (DESKTOP/jobbdator) är uppsatt och pushar automatiskt.

**Hemadatorn är INTE uppsatt ännu.**

**Why:** Användaren kom på detta 2026-04-20, åkte hem för att äta dumplings och skulle göra det sedan.

**How to apply:** PÅMINN användaren i början av nästa session att köra git-setup på hemadatorn:
```bash
cd ~/.claude
git init
git remote add origin https://github.com/SorbP/Claude_Status_Bar_Usage_colorblind.git
git config user.email "sorbpen@gmail.com"
git config user.name "SorbP"
git pull origin master
```
