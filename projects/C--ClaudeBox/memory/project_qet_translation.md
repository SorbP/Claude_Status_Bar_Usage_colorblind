---
name: QET Swedish translation pipeline
description: Översättning av QET-elementbiblioteket till svenska — pipeline klar, patch väntar på admin
type: project
originSessionId: bf444f34-967e-45d0-8e5e-bcaacad1eaa0
---
Bygger svensk översättning av QElectroTech:s elementbibliotek (6842 .elmt-filer i C:\Program Files\QElectroTech\elements\).

**Status: HELT KLAR 2026-04-22**

- 4 742 `.elmt`-elementfiler patchade med `<name lang="sv">`
- 1 034 `qet_directory`-kategorifiler patchade med `<name lang="sv">`
- Verifierat i QET — både elementnamn och kategorimappar visas på svenska

**Filer i C:\ClaudeBox\QElectroTech\:**
- `extract_english_names.py` — extraherar engelska namn → `element_names.json`
- `translate_names.py` — översätter elementnamn via Claude Haiku API
- `patch_element_files.py` — patchar .elmt-filer (Windows: attrib -r/+r istället för chmod)
- `translate_and_patch_categories.py` — översätter + patchar qet_directory-filer
- `translations.json` — ~4 750 översättningar (element + kategorier)
- `apl_mall.qet` — BH90-mall med 3 ark
- `validate_qet.py` — BH90-valideringsscript
- `new_apl_project.py` — projektgenerator med CLI-argument

**Why:** Bidra tillbaka till QET-communityn med en komplett svensk översättning.
**How to apply:** Projektet är avslutat. Inga fler åtgärder krävs.
