---
name: Linux migration research
description: Pågående research inför byte från Windows till Linux — hårdvara, distro, mjukvara
type: project
originSessionId: a82752c9-49c6-41b5-8146-9004020eb140
---
Användaren planerar att byta från Windows 10 till Linux på ASUS TUF Gaming FX505DV.

**Hårdvara bekräftad:**
- CPU: AMD Ryzen 7 3750H
- GPU: NVIDIA RTX 2060 Mobile (hybrid Optimus med AMD Vega 10 iGPU)
- RAM: 16GB
- Skärm: 1920x1080 @ 120Hz
- WiFi: Realtek 8822CE (rtw88-drivrutin, in-kernel, en tweakrad behövs)
- Ljud: Realtek ALC235 (perfekt Linux-stöd)
- Touchpad: ELAN1200 (fungerar)
- SSD: NVMe
- Secure Boot: PÅ — måste stängas av före installation
- Logitech Yeti GX mic (USB, plug and play)
- Wooting-tangentbord (Wootility AppImage, fungerar)
- RME Fireface 400 via FireWire (FFADO-drivrutin, TI-chipset bekräftat)

**Distro-beslut: CachyOS** (Arch-baserat, rolling, bäst gaming-prestanda, x86-64-v3 optimerade paket, BORE-scheduler) — Hyprland-edition
Alternativ: Nobara Linux (om CachyOS känns för avancerat)

**Desktop-miljö: Hyprland** (Wayland-compositor, tiling WM)
- Super-tangenten = Windows-knappen
- Super+1–0 = workspaces
- Super+V = flytande fönster toggle
- Flytande appar via windowrules: Thunar (filhanterare), comic-viewer etc.
- NVIDIA-patches ingår i CachyOS Hyprland-edition
- Alternativ: KDE Plasma Wayland om NVIDIA krånglar (officiellt stöd)

**Filhantering:**
- Yazi (terminal, bildförhandsvisning via Kitty Graphics Protocol, y = kopiera sökväg)
- Thunar (GUI, konfigureras som flytande = som Explorer)

**Statusfält/launcher:** Waybar + Wofi

**Terminal-stack beslutad:** Kitty + Zellij + Fish + Starship + JetBrains Mono Nerd Font + Yazi

**Gaming-status:**
- NVIDIA på Linux: ~80-85% av Windows-prestanda, sämre frame timing
- Proton + Steam: fungerar för ~85-90% av biblioteket
- Fungerar EJ: Valorant, League of Legends (Vanguard), PUBG
- envycontrol för Optimus-hantering: nvidia-läge för gaming, integrated för batterisparande

**Kritisk okänd: batteribegränsning**
Kör efter installation: `ls /sys/class/power_supply/BAT0/charge_control_end_threshold`
Finns filen → fungerar. Finns den inte → fungerar inte.
faustus-dkms bekräftat för FX505DV: tangentbordsbelysning + fläktlägen (ej batteri).

**Mjukvarustatus:**
- Steam/Proton: perfekt
- Discord: officiell klient, fungerar
- TeamSpeak: officiell Linux-klient (TS6) + server
- FSearch: Everything-ersättare (AUR)
- OneDrive: onedrive-abraunegg för backup/arkiv-användning
- Office 365: via webb (office.com), fungerar perfekt
- PlatformIO: pacman, fungerar
- Arduino IDE: arduino-ide-bin (AUR), fungerar
- VS Code: visual-studio-code-bin (AUR) — inte Code-OSS, krävs för Microsoft-extensions
- RME Fireface 400: FFADO + JACK/PipeWire
- Xbox Game Pass: fungerar EJ på Linux

**Färgblindhet (deuteranopi):**
Okabe-Ito-paletten används genomgående. Colorblind test-skript genererat (Python).
VS Code: GitHub Dark Colorblind-tema + token-overrides.
Kitty: okabe-ito-deutan.conf (genererad av agent).

**VIKTIGT — Linux-migrationen gäller ENBART laptopen (FX505DV), inte desktopen.**

**Desktop-maskin (stannar på Windows):**
- GPU: RTX 3090 med custom vattenkylingssystem (max 55°C under load)
- Precision-tunad undervolting: max 0.970V → effektiv klocka 2035MHz (upp från 1860MHz stock boost)
- Stannar på Windows permanent p.g.a. att NVIDIA Linux-drivrutinen inte stödjer custom voltkurva
- Voltage curve-bristen är en dealbreaker för den här maskinen

**OSD/monitoring på Linux (utrett):**
- RTSS-ersättare: MangoHud (nära ekvivalent, per-core CPU/GPU, frame time graph) ✅
- HWMonitor-ersättare: btop + nvtop ✅
- Afterburner-ersättare: GreenWithEnvy — fan curve + clock offset ✅, men ingen voltkurva ❌

**Why:** Användaren vill ha bättre kontroll, bättre terminal-upplevelse, och Linux-ekosystemets fördelar.
**How to apply:** Linux-migration = laptopen (FX505DV) med CachyOS. Desktop rörs inte. Fråga aldrig om att migrera desktopen till Linux.
