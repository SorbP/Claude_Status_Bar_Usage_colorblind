---
name: QET Swedish translation pipeline
description: Översättning av QET-elementbiblioteket till svenska — pipeline klar, patch väntar på admin
type: project
originSessionId: bf444f34-967e-45d0-8e5e-bcaacad1eaa0
---
Bygger svensk översättning av QElectroTech:s elementbibliotek (6842 .elmt-filer i C:\Program Files\QElectroTech\elements\).

**Status: KLAR — 4742 filer patchade 2026-04-22**

**Filer i C:\ClaudeBox\QElectroTech\:**
- `extract_english_names.py` — extraherar engelska namn → `element_names.json` (6842 poster, KLAR)
- `translate_names.py` — Claude Haiku API med prompt caching, batch 5 namn → `translations.json` (KLAR)
- `patch_element_files.py` — infogar `<name lang="sv">` i varje .elmt-fil (VÄNTAR PÅ ADMIN)
- `element_names.json` — 6842 poster extraherade
- `translations.json` — 3972 översättningar klara (4 korrupta poster hoppades över)
- `apl_mall.qet` — BH90-mall med 3 ark (Planritning E-001, Kretschema E-101, Huvudledningsschema E-201)
- `validate_qet.py` — BH90-valideringsscript
- `new_apl_project.py` — projektgenerator med CLI-argument

**Lösning på Windows-behörighetsproblem:**
`chmod` fungerade inte på Windows ACL. Löstes med `subprocess.run(['attrib', '-r', ...])` före skrivning och `+r` efteråt.

**Anthropic API-nyckel:**
Används för translate_names.py. Nyckeln är inte sparad — användaren anger den manuellt.
OBS: Tidigare nyckel exponerades i chatten — bör roteras på console.anthropic.com.

**Why:** Bidra tillbaka till QET-communityn med en komplett svensk översättning.
**How to apply:** Nästa steg = patch-steget. Om admin-frågan lösts, kör patch_element_files.py och verifiera i QET att svenska namn visas i elementbiblioteket.
